FROM python:3.10 as builder


ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . .
RUN poetry install --no-dev

CMD ["poetry", "run", "python", "main.py"]
