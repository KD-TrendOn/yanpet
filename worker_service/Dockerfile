FROM python:3.10

WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r /app/requirements.txt

CMD ["celery", "-A", "tasks", "worker", "--loglevel=info"]
