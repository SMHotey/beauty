from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment
from apps.auth_app.sms_service import SMSService
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_reminders():
    """Send reminders for appointments within 24 hours."""
    now = timezone.now()
    upcoming = Appointment.objects.filter(
        datetime_start__lte=now + timedelta(hours=24),
        datetime_start__gt=now,
        status__in=['pending', 'confirmed'],
        reminder_sent=False
    )
    count = 0
    for appt in upcoming:
        client_phone = appt.client.phone if appt.client else None
        if client_phone:
            services_list = ', '.join(s.service.name for s in appt.services.all())
            msg = f"Напоминание: запись на {appt.datetime_start.strftime('%d.%m.%Y %H:%M')} к мастеру {appt.master}. Услуги: {services_list}"
            logger.info(f"[REMINDER SMS] {client_phone}: {msg}")
            SMSService.send_code(client_phone, code=msg[:6])
        appt.reminder_sent = True
        appt.save(update_fields=['reminder_sent'])
        count += 1
    logger.info(f"Sent {count} reminders")
    return count
