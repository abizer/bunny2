import logging
import os
from typing import Any, List

import databases
import sqlalchemy
import toml
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)

# get the plugins
from plugins import Action, Lookup, load_plugins, plugin_registry

load_plugins()

# load config
DEFAULT_CONFIG_PATH = "runtime/config.toml"
config_root = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_root, DEFAULT_CONFIG_PATH)

with open(config_path, "r") as config_file:
    config = toml.load(config_file)
    DB_URL = config["db_url"]
    api_keys = set(config["api_keys"].values())

# some basic security to protect against randoms
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticated(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(status_code=401)


# connect to db
database = databases.Database(DB_URL)
metadata = sqlalchemy.MetaData()
urls = sqlalchemy.Table(
    "urls",
    metadata,
    sqlalchemy.Column("slug", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("url", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(DB_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


async def lookup_url_for_slug(slug: str) -> str:
    query = urls.select().where(urls.c.slug == slug)
    result = await database.fetch_one(query)
    return result["url"] if result else None


async def update_url_for_slug(slug: str, url: str) -> None:
    query = f"INSERT OR REPLACE INTO urls (slug, url) VALUES (:slug, :url)"
    await database.execute(query=query, values={"slug": slug, "url": url})


async def list_urls(n: int = 100):
    query = urls.select().limit(n)
    result = await database.fetch_all(query)
    return result


async def clear_urls(slug: str):
    query = urls.delete().where(urls.c.slug == slug)
    await database.execute(query)


# not sure why i'm reimplementing the builtin path based dispatcher logic
# to do it this way. ill figure out how to do that later
class Dispatcher:
    def _dispatch(self, processors: List[Any], path: str, payload: bytes):
        # first process all the regex-based rules
        for name, (pattern, fn) in processors.items():
            found = pattern.match(path)
            if found:
                logger.debug(f"dispatching {path} to {name}")
                try:
                    return fn(self, payload, *found.groups())
                except Exception as e:
                    logger.error(f"error processing {path} with {name}: {e}")
                    return e
            else:
                logger.debug(f"{name}/{pattern} did not match {path}")

    def get_action(self, path: str, payload: bytes) -> Action:
        action = self._dispatch(plugin_registry, path, payload)
        if not action:
            # if no regex rules matched, the default is to treat it as a slug
            # and try a database lookup
            logger.debug(f"{path} matched no rules, looking up as slug")
            return Lookup(path)
        else:
            # return whatever the action was if it matched something
            return action


def process_path(path: str, payload: bytes = None) -> str:
    # the api is always path -> (action, target)
    # where action can be ('lookup', 'redirect')
    action = Dispatcher().get_action(jsonable_encoder(path), payload)
    logger.debug(f"process_path: {path} => {action}")
    return action


def process_payload(path: str, payload: bytes) -> str:
    """convert the given payload to a url

    eventually this will be extended so that, e.g. files can be
    piped into the shorten endpoint and this function will write it
    to a pastebin and then return the URL for redirection.

    right now, it just assumes the payload is a URL and returns it.
    """
    is_url = payload[:4] == b"http"

    if is_url:
        return bytes.decode(payload).strip()
    else:
        return None


# ====== app routing logic =============================
@app.get("/list", dependencies=[Depends(authenticated)])
async def list():
    return await list_urls(n=100)


@app.get("/{path:path}")
async def bounce(path: str):
    action = process_path(path)

    url = None
    match action:
        case ("lookup", slug):
            url = await lookup_url_for_slug(slug)
        case ("redirect", target):
            url = target

    # default case is to google whatever was passed in
    if not url:
        logger.debug(f"action or lookup failed: googling {path}")
        google = plugin_registry["plugins.expansions.google"][1]
        _, url = google(None, None, query=path)

    logger.info(f"bounced {path} => {url}")
    return RedirectResponse(url)


@app.post("/{path:path}", dependencies=[Depends(authenticated)])
async def update(path: str, request: Request):
    logger.debug(f"update request: {path}")
    payload = await request.body()
    url = process_payload(path, payload)
    if not url:
        return Response(status_code=404)

    # action should be a ('lookup', slug)
    action = process_path(path, url)

    match action:
        case ("lookup", slug):
            logger.info(f"updating {slug} => {url}")
            await update_url_for_slug(slug, url)
            return RedirectResponse(url)

    return Response(status_code=404)


@app.delete("/{path:path}", dependencies=[Depends(authenticated)])
async def delete(path: str):
    action = process_path(path)

    match action:
        case ("lookup", slug):
            logger.info(f"deleting {slug}")
            await clear_urls(slug)
            return Response(status_code=200)

    return Response(status_code=404)


if __name__ == "__main__":
    from uvicorn import run

    run(app, host="127.0.0.1", port=8000)
