FROM python:3.10 as builder


ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV IS_DOCKER="true"

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . .
RUN poetry install

CMD ["poetry", "run", "bot"]
