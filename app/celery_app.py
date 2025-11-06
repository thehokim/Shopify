from celery import Celery
from app.celery_config import Config

# Create Celery instance
celery_app = Celery('shopify')

# Load configuration from config class
celery_app.config_from_object(Config)

# Auto-discover tasks in these modules
celery_app.autodiscover_tasks(['app.tasks'])


@celery_app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to test Celery"""
    print(f'Request: {self.request!r}')


if __name__ == '__main__':
    celery_app.start()