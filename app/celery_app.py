# 

from celery import Celery
from app.core.config import settings

celery_app = Celery(
  "worker",
  broker=settings.CELERY_BROKER_URL,
  backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
  task_serializer="json",
  accept_content=["json"],
  result_serializer="json",
  timezone="America/Sao_Paulo",
  enable_utc=True
)

# Definir as tasks agendadas (Beat) 
#celery_app.conf.beat_schedule ={}