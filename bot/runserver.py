import os
import sys
import logging
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

from webhook.app import app
from webhook.handlers import *


def main():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    

    host = "127.0.0.1"
    if os.getenv("IS_DOCKER"):
        host = "0.0.0.0"

    web.run_app(app, host=host, port=8005)


if __name__ == "__main__":
    main()
