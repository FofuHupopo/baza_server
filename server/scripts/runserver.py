import os
from dotenv import load_dotenv
from django.core.management import execute_from_command_line
from pathlib import Path


def main():
    DOTENV_PATH = Path(__file__).resolve().parent.parent / '.env'

    load_dotenv(DOTENV_PATH)

    port = os.getenv('PORT', 8000)
    host = os.getenv('HOST', 'localhost')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'universities.settings')
    execute_from_command_line(['manage.py', 'migrate'])
    execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])


if __name__ == "__main__":
    main()
