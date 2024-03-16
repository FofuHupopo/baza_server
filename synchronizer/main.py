import os
import uvicorn
import time
import shutil
import json

from pathlib import Path
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler

from synchronizer import MoySkaldSynchronizer


# DJANGO_MEDIA_PATH = Path("/Users/ilyazhukov/projects/projects/baza_store/server/media")
# DJANGO_MEDIA_PATH = Path("/home/ilya/baza/server/media")
# DJANGO_MEDIA_PATH = Path("/root/baza/server/server/media")
DJANGO_MEDIA_PATH = Path("/var/www/baza/server/server/media")
PRODUCT_MEDIA_PATH = Path("product_images")
ROOT_PATH = "сайт"
ROOT_DIRECTORY = Path(__file__).parent


app = FastAPI()
scheduler = BackgroundScheduler()

sync = MoySkaldSynchronizer(
    django_media_path=DJANGO_MEDIA_PATH,
    product_media_path=PRODUCT_MEDIA_PATH,
    root_path=ROOT_PATH,
    only_valid=True
)


@app.post("/synchronizer/webhook")
async def webhook(requestId: str, request: Request):
    body = await request.json()

    for event in body["events"]:
        action = event["action"]
        meta = event["meta"]

        if action in ("CREATE", "UPDATE"):
            uiid = meta.get("href").split("/")[-1]

            if not uiid:
                return {"status": "error"}, 400

            if meta["type"] == "product":
                print(f"sync product uiid: {uiid}")
                sync.sync_product_by_id(uiid)

            if meta["type"] == "bundle":
                print(f"sync bundle uiid: {uiid}")
                sync.sync_bundle_by_id(uiid)

    return {"status": "success"}, 200


@app.get("/synchronizer/sync_all")
def sync_all():
    sync.sync_all()
    return {"message": "Synchronization completed successfully."}


@app.get("/synchronizer/sync_product/{product_id}")
def sync_product_by_id(product_id: str):
    sync.sync_product_by_id(product_id)
    return {"message": f"Synchronization for product {product_id} completed successfully."}


@app.get("/synchronizer/sync_bundle/{bundle_id}")
def sync_bundle_by_id(bundle_id: str):
    sync.sync_bundle_by_id(bundle_id)
    return {"message": f"Synchronization for bundle {bundle_id} completed successfully."}


@app.post("/update/quantity")
async def update_quantity(request: Request):
    body = json.loads(await request.body())
    return {"status": "ok"}


if __name__ == "__main__":
    # uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)

    sync.sync_products()
    # sync.sync_bundles()
    # sync.sync_product_by_id("fe485046-edb1-11ed-0a80-034d00a3f03a")
