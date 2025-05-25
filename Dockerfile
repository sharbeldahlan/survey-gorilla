FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction

EXPOSE 8000
