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


config_path = "data/config.toml"
with open(config_path, "r") as f:
    config = toml.load(f)
    db_path = config["db_path"]
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
    print(f"deleting {slug}")
    db.clear(slug)

    return Response(content=slug, status_code=200)


@app.post("/{path:path}", dependencies=[Depends(authenticated)])
async def update(path: str, request: Request):
    payload = await request.body()
    print(payload)
    url = transform_payload_to_url(payload)
    print(url)
    slug = transform_path_to_slug(path, url)
    print(f"{path} => {slug} => {url}")

    db.update_url_for_slug(slug, url)

    return slug


@app.get("/{path:path}")
async def bounce(path: str):
    slug = transform_path_to_slug(path)
    print(f"path {path} => {slug}")
    url = db.lookup_url_for_slug(slug)
    print(f"slug {slug} => {url}")

    if url:
        return RedirectResponse(url)
    else:
        return Response(content=slug, status_code=404)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, reload=True)
