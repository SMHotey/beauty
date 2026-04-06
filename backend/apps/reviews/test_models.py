from decimal import Decimal

import pytest
from django.utils import timezone
from datetime import timedelta

from apps.reviews.models import Review


@pytest.mark.django_db
class TestReviewModel:
    def test_str(self, review):
        result = str(review)
        assert review.client.phone in result
        assert '5' in result

    def test_rating_choices(self, client, completed_appointment):
        from apps.appointments.models import Appointment, AppointmentService
        for rating in range(1, 6):
            past = timezone.now() - timedelta(days=10 + rating)
            appt = Appointment.objects.create(
                client=client, master=completed_appointment.master,
                datetime_start=past, datetime_end=past + timedelta(hours=1),
                status='completed', total_price=Decimal('1500.00'),
            )
            AppointmentService.objects.create(
                appointment=appt, service=completed_appointment.services.first().service,
                price_at_booking=Decimal('1500.00'), duration_at_booking=60,
            )
            r = Review.objects.create(
                client=client,
                appointment=appt,
                rating=rating,
                comment=f'Rating {rating}',
            )
            assert r.rating == rating

    def test_rating_validation_below_range(self, client, completed_appointment):
        from django.core.exceptions import ValidationError
        with pytest.raises((Exception, ValidationError)):
            r = Review(
                client=client,
                appointment=completed_appointment,
                rating=0,
                comment='Invalid',
            )
            r.full_clean()

    def test_rating_validation_above_range(self, client, completed_appointment):
        from django.core.exceptions import ValidationError
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
        with pytest.raises((Exception, ValidationError)):
            r = Review(
                client=client,
                appointment=appt2,
                rating=6,
                comment='Invalid',
            )
            r.full_clean()

    def test_one_to_one_appointment(self, client, completed_appointment):
        review = Review.objects.create(
            client=client,
            appointment=completed_appointment,
            rating=4,
            comment='Good',
        )
        assert completed_appointment.review == review

    def test_cascade_delete_client(self, client, completed_appointment):
        review = Review.objects.create(
            client=client,
            appointment=completed_appointment,
            rating=5,
            comment='Test',
        )
        client.delete()
        assert not Review.objects.filter(id=review.id).exists()

    def test_cascade_delete_appointment(self, client, completed_appointment):
        review = Review.objects.create(
            client=client,
            appointment=completed_appointment,
            rating=5,
            comment='Test',
        )
        completed_appointment.delete()
        assert not Review.objects.filter(id=review.id).exists()

    def test_ordering(self, client, completed_appointment):
        from django.utils import timezone
        from datetime import timedelta
        past = timezone.now() - timedelta(days=10)
        appt1 = completed_appointment
        appt1.datetime_start = past
        appt1.save()

        future_past = timezone.now() - timedelta(days=5)
        from apps.appointments.models import Appointment, AppointmentService
        appt2 = Appointment.objects.create(
            client=client, master=completed_appointment.master,
            datetime_start=future_past, datetime_end=future_past + timedelta(hours=1),
            status='completed', total_price=Decimal('1500.00'),
        )
        AppointmentService.objects.create(
            appointment=appt2, service=completed_appointment.services.first().service,
            price_at_booking=Decimal('1500.00'), duration_at_booking=60,
        )

        r1 = Review.objects.create(client=client, appointment=appt1, rating=3, comment='Old')
        r2 = Review.objects.create(client=client, appointment=appt2, rating=5, comment='New')
        reviews = list(Review.objects.all())
        assert reviews[0] == r2
        assert reviews[1] == r1
