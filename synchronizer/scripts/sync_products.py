from pathlib import Path
from app.synchronizer import MoySkaldSynchronizer


def main():
    PRODUCT_MEDIA_PATH = Path("product_images")
    ROOT_PATH = "сайт"
    ROOT_DIRECTORY = Path(__file__).parent


    sync = MoySkaldSynchronizer(
        product_media_path=PRODUCT_MEDIA_PATH,
        root_path=ROOT_PATH,
        only_valid=True
    )
    
    sync.sync_products()
    

if __name__ == "__main__":
    main()
