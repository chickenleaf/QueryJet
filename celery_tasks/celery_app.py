from celery import Celery
import os

# Initialize Celery
celery_app = Celery('celery_tasks', 
                    broker=os.environ.get("RABBITMQ_URL", "amqp://rabbitmq"),
                    backend='rpc://',
                    broker_connection_retry_on_startup=True)

# This will ensure that the shared tasks are registered
celery_app.autodiscover_tasks(['celery_tasks'], force=True)

# Optional: If you want to import the tasks module explicitly
import celery_tasks.tasks
