import sys
import os 
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from bunny2.db import DB
from bunny2.transform import transform_path_to_slug, transform_payload_to_url
from bunny2.plugins import load_plugins

from uvicorn import run

import toml
import logging

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
db = DB(db_path)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# some basic security to make sure randoms can't delete our slugs
def authenticated(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(status_code=401)


# load plugins
load_plugins()


@app.get("/list", dependencies=[Depends(authenticated)])
async def list():
    return db.list_all()


@app.delete("/{path:path}", dependencies=[Depends(authenticated)])
async def delete(path: str):
    slug = transform_path_to_slug(path)
    logging.info(f"deleting {slug}")
    db.clear(slug)

    return Response(content=slug, status_code=200)


@app.post("/{path:path}", dependencies=[Depends(authenticated)])
async def update(path: str, request: Request):
    payload = await request.body()
    url = transform_payload_to_url(payload)
    slug = transform_path_to_slug(path, url)
    logging.info(f"updating {path} => {slug} => {url}")

    db.update_url_for_slug(slug, url)

    return slug


@app.get("/{path:path}")
async def bounce(path: str):
    slug = transform_path_to_slug(path)
    url = db.lookup_url_for_slug(slug)
    logging.debug(f"getting {path} => {slug} => {url}")

    if url:
        return RedirectResponse(url)
    else:
        return Response(content=slug, status_code=404)


if __name__ == "__main__":
    run(app, host="127.0.0.1", port=8000)
