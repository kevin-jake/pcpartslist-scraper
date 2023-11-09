import os
from celery import Celery

CELERY_BROKER = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

celery =  Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)