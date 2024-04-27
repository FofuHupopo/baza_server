import os
from django.core.management import execute_from_command_line
from dotenv import load_dotenv
from pathlib import Path


def main():
    DOTENV_PATH = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(DOTENV_PATH)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'baza_store.settings')
    
    print(os.getenv("DB_PASSWORD"))

    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])


if __name__ == "__main__":
    main()
