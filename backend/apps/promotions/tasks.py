from celery import shared_task
from apps.auth_app.sms_service import SMSService
from apps.clients.models import Client
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_bulk_sms(phone_numbers, message):
    """Send SMS to multiple phone numbers."""
    results = []
    for phone in phone_numbers:
        logger.info(f"[SMS BROADCAST] {phone}: {message}")
        SMSService.send_code(phone, code=message[:6])
        results.append({'phone': phone, 'status': 'sent'})
    return {'total': len(results), 'results': results}
