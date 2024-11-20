from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from ninja_apikey.models import APIKey

logger = get_task_logger(__name__)


@shared_task
def delete_expired_api_keys():
    try:
        now = timezone.now()
        APIKey.objects.filter(expires_at__lt=now).delete()
        logger.info("Deleted expired API keys")
        return "Success"
    except Exception as e:
        logger.error(f"Task failed: {e}")
        raise
