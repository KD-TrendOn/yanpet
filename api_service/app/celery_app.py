from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest@rabbitmq//")

celery_app = Celery('api_service', broker=CELERY_BROKER_URL)
