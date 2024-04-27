import os
from dotenv import load_dotenv
from django.core.management import execute_from_command_line
from pathlib import Path


def main():
    DOTENV_PATH = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(DOTENV_PATH)
    
    if os.getenv("IS_DOCKER", "false") == "true":
        host = "0.0.0.0"
    else:
        host = os.getenv('HOST', "127.0.0.1")

    port = os.getenv('PORT', 8000)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'baza_store.settings')

    execute_from_command_line(['manage.py', 'runserver', f"{host}:{port}"])


if __name__ == "__main__":
    main()
