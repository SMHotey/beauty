import pytest
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.utils import timezone
from apps.services.models import ServiceCategory, Service
from apps.staff.models import Master, MasterService
from apps.clients.models import Client, FavoriteMaster
from apps.appointments.models import Appointment, AppointmentService
from apps.reviews.models import Review
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient, Setting


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')


@pytest.fixture
def staff_user(db):
    return User.objects.create_user(username='staff', password='staff123', email='staff@example.com', is_staff=True)


@pytest.fixture
def category(db):
    return ServiceCategory.objects.create(name='Hair', slug='hair', icon='scissors', order=1)


@pytest.fixture
def category2(db):
    return ServiceCategory.objects.create(name='Nails', slug='nails', icon='hand', order=2)


@pytest.fixture
def service(category):
    return Service.objects.create(
        category=category,
        name='Haircut',
        slug='haircut',
        base_duration_minutes=60,
        base_price=Decimal('1500.00'),
        gender_target='female',
        is_active=True,
    )


@pytest.fixture
def service2(category):
    return Service.objects.create(
        category=category,
        name='Hair Coloring',
        slug='hair-coloring',
        base_duration_minutes=90,
        base_price=Decimal('3000.00'),
        gender_target='female',
        is_active=True,
    )


@pytest.fixture
def master_user(db):
    return User.objects.create_user(
        username='master_user',
        first_name='Иван',
        last_name='Петров',
        email='master@example.com',
    )


@pytest.fixture
def master(master_user):
    return Master.objects.create(
        user=master_user,
        phone='+79001234567',
        bio='Опытный мастер',
        is_active=True,
        working_hours={
            '0': {'start': '09:00', 'end': '18:00'},
            '1': {'start': '09:00', 'end': '18:00'},
            '2': {'start': '09:00', 'end': '18:00'},
            '3': {'start': '09:00', 'end': '18:00'},
            '4': {'start': '09:00', 'end': '18:00'},
            '5': {'start': '09:00', 'end': '18:00'},
            '6': {'start': '09:00', 'end': '18:00'},
        },
        break_slots=[],
        vacations=[],
    )


@pytest.fixture
def master_service(master, service):
    return MasterService.objects.create(
        master=master,
        service=service,
        is_enabled=True,
    )


@pytest.fixture
def client(user):
    return Client.objects.create(user=user, phone='+79009999999')


@pytest.fixture
def client_no_user(db):
    return Client.objects.create(phone='+79008888888')


@pytest.fixture
def future_time():
    return timezone.now() + timedelta(days=2, hours=3)


@pytest.fixture
def appointment(client, master, service, future_time):
    appt = Appointment.objects.create(
        client=client,
        master=master,
        datetime_start=future_time,
        datetime_end=future_time + timedelta(hours=1),
        status='pending',
        total_price=Decimal('1500.00'),
    )
    AppointmentService.objects.create(
        appointment=appt,
        service=service,
        price_at_booking=Decimal('1500.00'),
        duration_at_booking=60,
    )
    return appt


@pytest.fixture
def completed_appointment(client, master, service):
    past_time = timezone.now() - timedelta(days=2)
    appt = Appointment.objects.create(
        client=client,
        master=master,
        datetime_start=past_time,
        datetime_end=past_time + timedelta(hours=1),
        status='completed',
        total_price=Decimal('1500.00'),
    )
    AppointmentService.objects.create(
        appointment=appt,
        service=service,
        price_at_booking=Decimal('1500.00'),
        duration_at_booking=60,
    )
    return appt


@pytest.fixture
def review(client, completed_appointment):
    return Review.objects.create(
        client=client,
        appointment=completed_appointment,
        rating=5,
        comment='Отлично!',
    )


@pytest.fixture
def active_promotion(service):
    today = timezone.now().date()
    promo = Promotion.objects.create(
        name='Summer Sale',
        description='20% off',
        discount_percent=Decimal('20.00'),
        start_date=today - timedelta(days=10),
        end_date=today + timedelta(days=10),
    )
    promo.applicable_services.add(service)
    return promo


@pytest.fixture
def expired_promotion():
    today = timezone.now().date()
    return Promotion.objects.create(
        name='Winter Sale',
        description='Expired',
        discount_percent=Decimal('15.00'),
        start_date=today - timedelta(days=60),
        end_date=today - timedelta(days=30),
    )


@pytest.fixture
def gift_certificate(db):
    return GiftCertificate.objects.create(
        nominal=Decimal('5000.00'),
        buyer_name='Test Buyer',
        recipient_email='test@example.com',
    )


@pytest.fixture
def blacklisted_client(client):
    return BlacklistedClient.objects.create(client=client, reason='Test reason')


@pytest.fixture
def setting(db):
    return Setting.objects.create(key='BONUS_PERCENT', value='10')
