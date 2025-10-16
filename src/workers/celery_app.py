from celery import Celery
from src.config.settings import settings

# Create Celery app
celery_app = Celery(
    "rag_engine",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.workers.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
)
