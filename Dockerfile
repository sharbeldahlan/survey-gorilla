FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]