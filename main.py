import importlib
import os
import re
import sqlite3
import sys
from typing import List, Any, Tuple
import logging

from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
import toml

from plugins import plugin_registry

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'runtime/config.toml'

config_root = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_root, DEFAULT_CONFIG_PATH)
if len(sys.argv) > 1:
    config_path = sys.argv[1]

with open(config_path, 'r') as config_file:
    config = toml.load(config_file)
    db_path = os.path.join(config_root, config["db_path"])
    api_keys = set(config["api_keys"].values())

app = FastAPI()

# type alias this, it's a hack so sorry
Tdb = Tuple[sqlite3.Connection, sqlite3.Cursor]

# some basic security to protect against randoms
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def authenticated(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(status_code=401)
    
def get_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        yield conn, cursor 
    finally:
        conn.close()

def lookup_url_for_slug(db: Tdb, slug: str) -> str:
        _, cursor = db
        cursor.execute("SELECT url FROM urls WHERE slug=?", (slug,))
        result = cursor.fetchone()

        return result[0] if result else None

def update_url_for_slug(db: Tdb, slug: str, url: str) -> None:
    conn, cursor = db
    cursor.execute(
        "INSERT OR REPLACE INTO urls (slug, url) VALUES (?, ?)", (slug, url)
    )
    conn.commit()

def list_urls(db: Tdb, n: int = 100):
    _, cursor = db
    cursor.execute("SELECT slug, url FROM urls LIMIT ?", (n,))
    result = cursor.fetchall()

    return result

def clear_urls(db: Tdb, slug: str):
    conn, cursor = db
    cursor.execute("DELETE FROM urls WHERE slug=?", (slug,))
    conn.commit()
    

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

        # default case: reflection
        return path

    def run(self, path: str, payload: bytes):
        return self._dispatch(plugin_registry, path, payload)


def path_to_url(db: Tdb, path: str, payload: bytes = None) -> str:
    """converts the given path to a slug for database lookup

    to maintain consistency, the same function is used on both read and write paths.
    on the write path, the additional context from the payload may be used for deriving
      new slugs on known patterns.

    default behavior is that the request path is the slug
    transform_path_to_slug("exploring") -> "exploring"

    slugs can be aliased to other slugs
    transform_path_to_slug("h5") -> "/hobby/5"

    can implement a pattern-based shorturl generator
    transform_path_to_slug("shorten", "https://docs.google.com/...") -> "/g/ef45gh"

    do arbitrary work, like curl-able pastebin
    transform_path_to_slug("paste", <file contents>) -> "/p/abd4f5b32"
    transform_path_to_slug("pasted/debuglogs", <file contents>) -> "/p/20230823/debuglogs"

    it's expected that the single argument call produces only readable slugs and the
    double argument call produces only writable slugs
    """

    dispatch = Dispatcher().run(path, payload)
    url = dispatch if dispatch.startswith('http') else lookup_url_for_slug(db, dispatch)
    return url
    


def payload_to_url(payload: bytes) -> str:
    """convert the given payload to a url

    eventually this will be extended so that, e.g. files can be
    piped into the shorten endpoint and this function will write it
    to a pastebin and then return the URL for redirection.

    right now, it just assumes the payload is a URL and returns it.
    """
    is_url = payload[:4] == b"http"

    if is_url:
        return bytes.decode(payload).strip()



@app.get("/list", dependencies=[Depends(authenticated)])
async def list(db: Tdb = Depends(get_db)):
    return list_urls(db)


@app.delete("/{path:path}", dependencies=[Depends(authenticated)])
async def delete(path: str, db: Tdb = Depends(get_db)):
    slug = path_to_url(path)
    logger.info(f"deleting {slug}")
    db.clear(slug)

    return Response(content=slug, status_code=200)


@app.post("/{path:path}", dependencies=[Depends(authenticated)])
async def update(path: str, request: Request, db: Tdb = Depends(get_db)):
    payload = await request.body()
    url = payload_to_url(payload)
    slug = path_to_url(path, url)
    logger.info(f"updating {path} => {slug} => {url}")

    db.update_url_for_slug(slug, url)

    return slug


@app.get("/{path:path}")
async def bounce(path: str, db: Tdb = Depends(get_db)):
    url = path_to_url(db, path)
    # url = db.lookup_url_for_slug(slug)
    logger.debug(f"getting {path} => {url}")

    # if url:
    return RedirectResponse(url)
    # else:
    #    return Response(content=slug, status_code=404)


if __name__ == "__main__":
    from uvicorn import run
    run(app, host="127.0.0.1", port=8000)
