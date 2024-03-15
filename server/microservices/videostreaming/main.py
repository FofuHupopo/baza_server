import cv2
import time
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse


app = FastAPI()
templates = Jinja2Templates(directory="templates")
VIDEO_URL = str(Path("./static/video.mp4"))


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
