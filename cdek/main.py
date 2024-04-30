import json
import uvicorn

from pathlib import Path
from fastapi import FastAPI, Request


app = FastAPI()


@app.get("/")
async def update_quantity(request: Request):
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)
