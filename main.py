from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from uvicorn import run
from bunny2.db import lookup_url_for_slug, update_url_for_slug, list_all
from bunny2.transform import transform_path_to_slug, transform_payload_to_url

import logging
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
@app.get("/list")
async def list():
    return list_all()


@app.get("/{path:path}")
async def bounce(path: str):
    slug = transform_path_to_slug(path)
    print(f"path {path} => {slug}")
    url = lookup_url_for_slug(slug)
    print(f"slug {slug} => {url}")

    if url:
        return RedirectResponse(url)
    else:
        return Response(content=slug, status_code=404)
    
@app.post("/{path:path}")
async def update(path: str, request: Request):
    payload = await request.body()
    print(payload)
    url = transform_payload_to_url(payload)
    print(url)
    slug = transform_path_to_slug(path, url)
    print(f"{path} => {slug} => {url}")

    update_url_for_slug(slug, url)
    
    return slug

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, reload=True)
