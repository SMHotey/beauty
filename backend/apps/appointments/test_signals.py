from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentService
from apps.appointments.signals import award_bonus_on_completion
from apps.clients.models import Client
from apps.promotions.models import Setting


@pytest.mark.django_db
class TestBonusAwardSignal:
    def test_bonus_awarded_on_completion(self, client, master, service):
        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        client.refresh_from_db()
        assert client.bonus_balance == 0

        appt.status = 'completed'
        appt.save()

        client.refresh_from_db()
        assert client.bonus_balance == 50

    def test_bonus_uses_custom_percent(self, client, master, service, setting):
        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        appt.status = 'completed'
        appt.save()

        client.refresh_from_db()
        assert client.bonus_balance == 100

    def test_no_bonus_for_zero_price(self, client, master):
        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('0.00'),
        )
        appt.status = 'completed'
        appt.save()

        client.refresh_from_db()
        assert client.bonus_balance == 0

    def test_no_bonus_for_guest(self, master, service):
        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=None, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        appt.status = 'completed'
        appt.save()

    def test_no_bonus_on_creation(self, client, master, service):
        future = timezone.now() + timedelta(days=1)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
            status='completed', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        client.refresh_from_db()
        assert client.bonus_balance == 0

    def test_no_double_bonus(self, client, master, service):
        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=client, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        appt.status = 'completed'
        appt.save()

        appt.comment = 'Updated'
        appt.save()

        client.refresh_from_db()
        assert client.bonus_balance == 50

    def test_referral_bonus(self, master, service):
        referrer = Client.objects.create(phone='+79001111111')
        referred = Client.objects.create(phone='+79002222222', referred_by=referrer)

        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=referred, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        appt.status = 'completed'
        appt.save()

        referrer.refresh_from_db()
        assert referrer.bonus_balance == 500

        referred.refresh_from_db()
        assert referred.bonus_balance == 50

    def test_referral_bonus_custom_amount(self, master, service):
        Setting.objects.create(key='REFERRAL_BONUS', value='1000')
        referrer = Client.objects.create(phone='+79003333333')
        referred = Client.objects.create(phone='+79004444444', referred_by=referrer)

        past = timezone.now() - timedelta(days=2)
        appt = Appointment.objects.create(
            client=referred, master=master,
            datetime_start=past, datetime_end=past + timedelta(hours=1),
            status='pending', total_price=Decimal('1000.00'),
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        appt.status = 'completed'
        appt.save()

        referrer.refresh_from_db()
        assert referrer.bonus_balance == 1000


@pytest.mark.django_db
class TestMasterRatingSignal:
    def test_rating_updated_on_review_create(self, client, completed_appointment):
        master = completed_appointment.master
        assert master._cached_rating is None

        from apps.reviews.models import Review
        Review.objects.create(
            client=client, appointment=completed_appointment,
            rating=4, comment='Good',
        )

        master.refresh_from_db()
        assert master._cached_rating == 4.0

    def test_rating_updated_on_review_delete(self, client, completed_appointment):
        from apps.reviews.models import Review
        review = Review.objects.create(
            client=client, appointment=completed_appointment,
            rating=5, comment='Great',
        )
        master = completed_appointment.master
        master.refresh_from_db()
        assert master._cached_rating == 5.0

        review.delete()
        master.refresh_from_db()
        assert master._cached_rating is None

    def test_rating_averaged(self, client, completed_appointment):
        from apps.reviews.models import Review
        from apps.appointments.models import Appointment, AppointmentService

        past2 = timezone.now() - timedelta(days=3)
        appt2 = Appointment.objects.create(
            client=client, master=completed_appointment.master,
            datetime_start=past2, datetime_end=past2 + timedelta(hours=1),
            status='completed', total_price=Decimal('1500.00'),
        )
        AppointmentService.objects.create(
            appointment=appt2, service=completed_appointment.services.first().service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        Review.objects.create(client=client, appointment=completed_appointment, rating=5, comment='A')
        Review.objects.create(client=client, appointment=appt2, rating=3, comment='B')

        master = completed_appointment.master
        master.refresh_from_db()
        assert master._cached_rating == 4.0
