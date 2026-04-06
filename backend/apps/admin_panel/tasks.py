from celery import shared_task
from apps.auth_app.sms_service import SMSService


@shared_task
def send_bulk_sms(phones, message):
    for phone in phones:
        SMSService.send_code(phone, code='BROADCAST')
    return {'sent': len(phones)}
