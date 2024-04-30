import uvicorn
import cv2
import time
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse, Response


app = FastAPI()
templates = Jinja2Templates(directory="templates")

CACHE_LIFETIME = timedelta(hours=6)
VIDEO_NAME = "video.mp4"
VIDEO_URL = str(Path(f"./static/{VIDEO_NAME}"))


def gen_video():
    video = cv2.VideoCapture(VIDEO_URL)

    while True:
        success, frame = video.read()

        if not success:
            video = cv2.VideoCapture(VIDEO_URL)
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/video")
def video():
    return StreamingResponse(gen_video(), media_type='multipart/x-mixed-replace; boundary=frame')


blob_cache = {
    "cached": None,
    "time": CACHE_LIFETIME,
    "last_time_cached": datetime.now()
}


@app.get("/blob")
def video():
    if not blob_cache["cached"] or blob_cache["last_time_cached"] + blob_cache["time"] < datetime.now():
        with open(VIDEO_URL, "rb") as video:
            video_bytes = video.read()

        response = Response(content=video_bytes)
        response.headers["Content-Disposition"] = f"attachment; filename={VIDEO_NAME}"
        blob_cache["cached"] = response
        blob_cache["last_time_cached"] = datetime.now()

    return blob_cache["cached"]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
