from celery import Celery

from ..core.config import settings

celery_app = Celery(
    "questionnaire_agent",
    broker=settings.worker_broker_url,
    backend=settings.worker_result_backend,
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["src.workers"])
