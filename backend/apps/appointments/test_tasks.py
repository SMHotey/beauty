from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

import pytest
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentService
from apps.appointments.tasks import send_reminders
from apps.clients.models import Client
from apps.staff.models import Master


@pytest.mark.django_db
class TestSendRemindersTask:
    def test_sends_reminder_for_upcoming_appointment(self, client, master, service):
        upcoming = timezone.now() + timedelta(hours=12)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=upcoming, datetime_end=upcoming + timedelta(hours=1),
            status='pending', reminder_sent=False,
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        with patch('apps.appointments.tasks.SMSService') as mock_sms:
            mock_sms.send_code.return_value = '123456'
            result = send_reminders()

        assert result == 1
        appt.refresh_from_db()
        assert appt.reminder_sent is True
        mock_sms.send_code.assert_called_once()

    def test_does_not_send_for_already_sent(self, client, master, service):
        upcoming = timezone.now() + timedelta(hours=12)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=upcoming, datetime_end=upcoming + timedelta(hours=1),
            status='pending', reminder_sent=True,
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        with patch('apps.appointments.tasks.SMSService') as mock_sms:
            result = send_reminders()

        assert result == 0
        mock_sms.send_code.assert_not_called()

    def test_does_not_send_for_past_appointment(self, client, master, service):
        past = timezone.now() - timedelta(hours=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', reminder_sent=False,
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        with patch('apps.appointments.tasks.SMSService') as mock_sms:
            result = send_reminders()

        assert result == 0

    def test_does_not_send_for_completed_appointment(self, client, master, service):
        upcoming = timezone.now() + timedelta(hours=12)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=upcoming, datetime_end=upcoming + timedelta(hours=1),
            status='completed', reminder_sent=False,
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        with patch('apps.appointments.tasks.SMSService') as mock_sms:
            result = send_reminders()

        assert result == 0

    def test_does_not_send_for_guest_without_phone(self, master, service):
        upcoming = timezone.now() + timedelta(hours=12)
        appt = Appointment.objects.create(
            client=None, master=master,
            datetime_start=upcoming, datetime_end=upcoming + timedelta(hours=1),
            status='pending', reminder_sent=False,
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        with patch('apps.appointments.tasks.SMSService') as mock_sms:
            result = send_reminders()

        assert result == 1
        appt.refresh_from_db()
        assert appt.reminder_sent is True
        mock_sms.send_code.assert_not_called()

    def test_sends_multiple_reminders(self):
        user1 = __import__('django.contrib.auth.models', fromlist=['User']).User.objects.create_user(username='rem1', password='pass')
        user2 = __import__('django.contrib.auth.models', fromlist=['User']).User.objects.create_user(username='rem2', password='pass')
        master_user = __import__('django.contrib.auth.models', fromlist=['User']).User.objects.create_user(username='rem_master', password='pass')
        master = Master.objects.create(user=master_user, phone='+79009999999', is_active=True)
        c1 = Client.objects.create(user=user1, phone='+79001111111')
        c2 = Client.objects.create(user=user2, phone='+79002222222')

        upcoming = timezone.now() + timedelta(hours=12)
        appt1 = Appointment.objects.create(
            client=c1, master=master,
            datetime_start=upcoming, datetime_end=upcoming + timedelta(hours=1),
            status='pending', reminder_sent=False,
        )
        appt2 = Appointment.objects.create(
            client=c2, master=master,
            datetime_start=upcoming + timedelta(hours=2), datetime_end=upcoming + timedelta(hours=3),
            status='confirmed', reminder_sent=False,
        )

        with patch('apps.appointments.tasks.SMSService') as mock_sms:
            mock_sms.send_code.return_value = '123456'
            result = send_reminders()

        assert result == 2
        assert mock_sms.send_code.call_count == 2


@pytest.mark.django_db
class TestBulkSmsTask:
    def test_send_bulk_sms_appointments(self):
        from apps.promotions.tasks import send_bulk_sms

        phones = ['+79001111111', '+79002222222', '+79003333333']
        message = 'Test message'

        with patch('apps.promotions.tasks.SMSService') as mock_sms:
            mock_sms.send_code.return_value = '123456'
            result = send_bulk_sms(phones, message)

        assert result['total'] == 3
        assert len(result['results']) == 3
        assert mock_sms.send_code.call_count == 3

    def test_send_bulk_sms_empty_list(self):
        from apps.promotions.tasks import send_bulk_sms

        with patch('apps.promotions.tasks.SMSService') as mock_sms:
            result = send_bulk_sms([], 'Test')

        assert result['total'] == 0
        assert result['results'] == []
        mock_sms.send_code.assert_not_called()

    def test_send_bulk_sms_admin_panel(self):
        from apps.admin_panel.tasks import send_bulk_sms as admin_send_bulk_sms

        phones = ['+79001111111', '+79002222222']

        with patch('apps.admin_panel.tasks.SMSService') as mock_sms:
            result = admin_send_bulk_sms(phones, 'Broadcast')

        assert result['sent'] == 2
        assert mock_sms.send_code.call_count == 2
