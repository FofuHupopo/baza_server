import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


DB_PATH = os.getenv("DB_PATH")

if DB_PATH is None:
    raise ValueError("Не указан путь к базе данных в .env файле.")

engine = create_engine(DB_PATH)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
