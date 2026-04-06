from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from apps.services.models import Service, ServiceCategory
from apps.staff.models import Master, MasterService


@pytest.mark.django_db
class TestMasterModel:
    def test_str_with_full_name(self):
        user = User.objects.create_user(username='master1', first_name='Иван', last_name='Петров')
        master = Master.objects.create(user=user, phone='+79001111111', is_active=True)
        assert str(master) == 'Иван Петров'

    def test_str_without_full_name(self):
        user = User.objects.create_user(username='master_phone')
        master = Master.objects.create(user=user, phone='+79002222222', is_active=True)
        assert str(master) == 'master_phone'

    def test_default_is_active(self):
        user = User.objects.create_user(username='master3')
        master = Master.objects.create(user=user, phone='+79003333333')
        assert master.is_active is True

    def test_default_working_hours(self):
        user = User.objects.create_user(username='master4')
        master = Master.objects.create(user=user, phone='+79004444444')
        assert master.working_hours == {}

    def test_default_break_slots(self):
        user = User.objects.create_user(username='master5')
        master = Master.objects.create(user=user, phone='+79005555555')
        assert master.break_slots == []

    def test_default_vacations(self):
        user = User.objects.create_user(username='master6')
        master = Master.objects.create(user=user, phone='+79006666666')
        assert master.vacations == []

    def test_rating_no_reviews(self, master):
        assert master.rating is None

    def test_rating_with_reviews(self, master, client, service):
        from apps.appointments.models import Appointment, AppointmentService
        from apps.reviews.models import Review
        from django.utils import timezone
        from datetime import timedelta

        past = timezone.now() - timedelta(days=5)
        appt1 = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='completed', total_price=Decimal('1500.00'),
        )
        AppointmentService.objects.create(appointment=appt1, service=service, price_at_booking=Decimal('1500.00'), duration_at_booking=60)
        Review.objects.create(client=client, appointment=appt1, rating=5, comment='Great')

        past2 = timezone.now() - timedelta(days=3)
        appt2 = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past2, datetime_end=past2 + timedelta(hours=1),
            status='completed', total_price=Decimal('1500.00'),
        )
        AppointmentService.objects.create(appointment=appt2, service=service, price_at_booking=Decimal('1500.00'), duration_at_booking=60)
        Review.objects.create(client=client, appointment=appt2, rating=3, comment='OK')

        assert master.rating == 4.0
        assert master.review_count == 2

    def test_one_to_one_user(self):
        user = User.objects.create_user(username='master7')
        master = Master.objects.create(user=user, phone='+79007777777')
        assert user.master_profile == master


@pytest.mark.django_db
class TestMasterServiceModel:
    def test_str(self, master, service):
        ms = MasterService.objects.create(master=master, service=service, is_enabled=True)
        assert str(ms) == f'{master} — {service}'

    def test_price_uses_custom(self, master, service):
        ms = MasterService.objects.create(
            master=master, service=service,
            custom_price=Decimal('2000.00'), is_enabled=True,
        )
        assert ms.price == Decimal('2000.00')

    def test_price_uses_service_default(self, master, service):
        ms = MasterService.objects.create(master=master, service=service, is_enabled=True)
        assert ms.price == service.base_price

    def test_duration_uses_custom(self, master, service):
        ms = MasterService.objects.create(
            master=master, service=service,
            custom_duration_minutes=120, is_enabled=True,
        )
        assert ms.duration_minutes == 120

    def test_duration_uses_service_default(self, master, service):
        ms = MasterService.objects.create(master=master, service=service, is_enabled=True)
        assert ms.duration_minutes == service.base_duration_minutes

    def test_unique_together(self, master, service):
        MasterService.objects.create(master=master, service=service, is_enabled=True)
        with pytest.raises(Exception):
            MasterService.objects.create(master=master, service=service, is_enabled=False)

    def test_is_enabled_default(self, master, service):
        ms = MasterService.objects.create(master=master, service=service)
        assert ms.is_enabled is True
