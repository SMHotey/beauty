from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentService
from apps.appointments.utils import get_available_slots
from apps.clients.models import Client
from apps.staff.models import Master, MasterService


@pytest.mark.django_db
class TestAppointmentModel:
    def test_str_with_client(self, client, master):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        assert str(appt) == f'{client.phone} — {master} — {future}'

    def test_str_without_client(self, master):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=None, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        assert 'Гость' in str(appt)

    def test_default_status(self, client, master):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
        )
        assert appt.status == 'pending'

    def test_default_total_price(self, client, master):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
        )
        assert appt.total_price == 0

    def test_default_reminder_sent(self, client, master):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
        )
        assert appt.reminder_sent is False

    def test_total_price_calculated_on_save(self, client, master, service):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )
        appt.save()
        assert appt.total_price == Decimal('1500.00')

    def test_total_price_multiple_services(self, client, master, service, service2):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=2),
            status='pending',
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )
        AppointmentService.objects.create(
            appointment=appt, service=service2,
            price_at_booking=Decimal('3000.00'), duration_at_booking=90,
        )
        appt.save()
        assert appt.total_price == Decimal('4500.00')

    def test_status_choices(self, client, master):
        future = timezone.now() + timedelta(days=1)
        for status_code, _ in Appointment.STATUS_CHOICES:
            appt = Appointment.objects.create(
                client=client, master=master,
                datetime_start=future, datetime_end=future + timedelta(hours=1),
                status=status_code,
            )
            assert appt.status == status_code

    def test_ordering(self, client, master):
        t1 = timezone.now() + timedelta(days=1)
        t2 = timezone.now() + timedelta(days=2)
        appt1 = Appointment.objects.create(
            client=client, master=master,
            datetime_start=t1, datetime_end=t1 + timedelta(hours=1),
        )
        appt2 = Appointment.objects.create(
            client=client, master=master,
            datetime_start=t2, datetime_end=t2 + timedelta(hours=1),
        )
        appts = list(Appointment.objects.all())
        assert appts[0] == appt2
        assert appts[1] == appt1


@pytest.mark.django_db
class TestAppointmentServiceModel:
    def test_str(self, appointment):
        appt_service = appointment.services.first()
        assert str(appt_service) is not None
        assert 'Haircut' in str(appt_service)

    def test_cascade_delete_appointment(self, client, master, service):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
        )
        appt_svc = AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )
        appt.delete()
        assert not AppointmentService.objects.filter(id=appt_svc.id).exists()


@pytest.mark.django_db
class TestSlotGeneration:
    def test_slots_generated_for_working_day(self, master, service):
        MasterService.objects.create(master=master, service=service, is_enabled=True)
        future_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        slots = get_available_slots(master.id, future_date, [service.id])
        assert len(slots) > 0

    def test_no_slots_for_non_working_day(self, master, service):
        MasterService.objects.create(master=master, service=service, is_enabled=True)
        future_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        master.working_hours = {}
        master.save()
        slots = get_available_slots(master.id, future_date, [service.id])
        assert slots == []

    def test_no_slots_for_nonexistent_master(self, service):
        future_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        slots = get_available_slots(99999, future_date, [service.id])
        assert slots == []

    def test_slots_respect_working_hours(self, master, service):
        MasterService.objects.create(master=master, service=service, is_enabled=True)
        future_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        slots = get_available_slots(master.id, future_date, [service.id])
        for slot in slots:
            hour = int(slot[11:13])
            assert 9 <= hour < 18

    def test_slots_format(self, master, service):
        MasterService.objects.create(master=master, service=service, is_enabled=True)
        future_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        slots = get_available_slots(master.id, future_date, [service.id])
        for slot in slots:
            assert 'T' in slot
            assert len(slot) == 19
