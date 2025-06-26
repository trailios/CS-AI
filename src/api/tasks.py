from celery import Celery
import time

celery_app = Celery(
    "src.api.tasks",
    broker="redis://144.76.218.98:6379/0",
    backend="redis://144.76.218.98:6379/0"
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

@celery_app.task
def solve(inputd) -> str:
    time.sleep(2)
    return "example solved - " + inputd