from pathlib import Path
from dotenv import load_dotenv
from app.synchronizer import MoySkaldSynchronizer


def main():
    load_dotenv()

    PRODUCT_MEDIA_PATH = Path("product_images")
    ROOT_PATH = "сайт"

    sync = MoySkaldSynchronizer(
        product_media_path=PRODUCT_MEDIA_PATH,
        root_path=ROOT_PATH,
        only_valid=True
    )
    
    sync.sync_products()
    

if __name__ == "__main__":
    main()
