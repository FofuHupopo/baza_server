import os
import uvicorn
import time
import shutil

from pathlib import Path
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler

from synchronizer import MoySkaldSynchronizer


DJANGO_MEDIA_PATH = Path("/Users/ilyazhukov/projects/projects/baza_store/server/media")
PRODUCT_MEDIA_PATH = Path("product_images")
VALID_ROOT_PATH = {
    "женское": "women",
    "мужское": "man",
    "детское": "children",
    "тест для сайта": "test-for-site"
}
ROOT_DIRECTORY = Path(__file__).parent


app = FastAPI()
scheduler = BackgroundScheduler()

sync = MoySkaldSynchronizer(
    django_media_path=DJANGO_MEDIA_PATH,
    product_media_path=PRODUCT_MEDIA_PATH,
    valid_root_path=VALID_ROOT_PATH,
    only_valid=True
)


@app.on_event("startup")
def start_scheduler():
    # scheduler.add_job(sync_products, "interval", seconds=10)
    scheduler.start()

    
@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()


@app.post("synchronizer/webhook")
async def webhook(request: Request):
    body = await request.json()

    if "event" in body and "meta" in body:
        event_type = body["event"]
        meta = body["meta"]

        if event_type == "PRODUCT_CREATED" or event_type == "PRODUCT_UPDATED":
            product_id = meta.get("uuid")
            if product_id:
                sync.sync_product_by_id(product_id)

        elif event_type == "BUNDLE_CREATED" or event_type == "BUNDLE_UPDATED":
            bundle_id = meta.get("uuid")
            if bundle_id:
                sync.sync_bundle_by_id(bundle_id)

    return {"status": "success"}


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


if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=4444, reload=True)

    # sync.sync_products()
    sync.sync_bundles()
