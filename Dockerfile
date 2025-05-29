FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction

RUN mkdir -p /app/staticfiles

# collect static files ahead of time
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]