import os
import uvicorn
from dotenv import load_dotenv
import json

from fastapi.openapi.docs import get_swagger_ui_html
from pathlib import Path
from fastapi import FastAPI, Request
from apscheduler.schedulers.background import BackgroundScheduler

from app.synchronizer import MoySkaldSynchronizer


PRODUCT_MEDIA_PATH = Path("product_images")
ROOT_PATH = "сайт"
ROOT_DIRECTORY = Path(__file__).parent


app = FastAPI()
scheduler = BackgroundScheduler()

sync = MoySkaldSynchronizer(
    product_media_path=PRODUCT_MEDIA_PATH,
    root_path=ROOT_PATH,
    only_valid=True
)


@app.get("/swagger", include_in_schema=False)
async def get_documentation(request: Request):
    return get_swagger_ui_html(openapi_url="/service/synchronizer/" + "/openapi.json", title="Swagger")


@app.post("/sync/webhook")
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


@app.get("/sync/sync_all")
def sync_all():
    sync.sync_all()
    return {"message": "Synchronization completed successfully."}


@app.get("/sync/sync_product/{product_id}")
def sync_product_by_id(product_id: str):
    sync.sync_product_by_id(product_id)
    return {"message": f"Synchronization for product {product_id} completed successfully."}


@app.get("/sync/sync_bundle/{bundle_id}")
def sync_bundle_by_id(bundle_id: str):
    sync.sync_bundle_by_id(bundle_id)
    return {"message": f"Synchronization for bundle {bundle_id} completed successfully."}


@app.post("/update/quantity")
async def update_quantity(request: Request):
    body = json.loads(await request.body())
    return {"message": "not released"}


def main():
    load_dotenv()

    host = "127.0.0.1"
    if os.getenv("IS_DOCKER"):
        host = "0.0.0.0"

    uvicorn.run("main:app", host=host, port=8004, reload=True)


if __name__ == "__main__":
    main()
