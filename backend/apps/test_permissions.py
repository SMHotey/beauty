from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from apps.appointments.models import Appointment, AppointmentService
from apps.clients.models import Client
from apps.services.models import Service, ServiceCategory
from apps.staff.models import Master


ENDPOINTS = {
    'admin_panel': [
        ('GET', '/api/v1/admin-panel/dashboard/stats/'),
        ('GET', '/api/v1/admin-panel/masters/'),
        ('GET', '/api/v1/admin-panel/calendar/'),
        ('GET', '/api/v1/admin-panel/appointments/'),
        ('GET', '/api/v1/admin-panel/reports/sales/'),
    ],
    'client_profile': [
        ('GET', '/api/v1/clients/profile/me/'),
        ('PATCH', '/api/v1/clients/profile/update_me/'),
    ],
    'favorites': [
        ('GET', '/api/v1/clients/favorites/'),
        ('POST', '/api/v1/clients/favorites/'),
    ],
    'gift_certificates_list': [
        ('GET', '/api/v1/promotions/gift-certificates/'),
    ],
    'blacklist': [
        ('GET', '/api/v1/promotions/blacklist/'),
    ],
}


@pytest.mark.django_db
class TestAdminPermissions:
    def test_admin_can_access_all_endpoints(self, admin_user):
        client = APIClient()
        client.force_authenticate(user=admin_user)
        for method, url in ENDPOINTS['admin_panel']:
            response = client.generic(method, url)
            assert response.status_code in [200, 201, 400], f'{method} {url} returned {response.status_code}'

    def test_regular_user_cannot_access_admin(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        for method, url in ENDPOINTS['admin_panel']:
            response = client.generic(method, url)
            assert response.status_code in [401, 403], f'{method} {url} should be forbidden but got {response.status_code}'

    def test_unauthenticated_cannot_access_admin(self):
        client = APIClient()
        for method, url in ENDPOINTS['admin_panel']:
            response = client.generic(method, url)
            assert response.status_code in [401, 403], f'{method} {url} should be forbidden but got {response.status_code}'

    def test_staff_user_can_access_admin(self, staff_user):
        client = APIClient()
        client.force_authenticate(user=staff_user)
        for method, url in ENDPOINTS['admin_panel']:
            response = client.generic(method, url)
            assert response.status_code in [200, 201, 400], f'{method} {url} returned {response.status_code}'


@pytest.mark.django_db
class TestClientProfilePermissions:
    def test_authenticated_can_access_profile(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/clients/profile/me/')
        assert response.status_code == 200

    def test_unauthenticated_cannot_access_profile(self):
        client = APIClient()
        response = client.get('/api/v1/clients/profile/me/')
        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestFavoritesPermissions:
    def test_authenticated_can_access_favorites(self, user):
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/clients/favorites/')
        assert response.status_code == 200

    def test_unauthenticated_cannot_access_favorites(self):
        client = APIClient()
        response = client.get('/api/v1/clients/favorites/')
        assert response.status_code in [401, 403]


@pytest.mark.django_db
class TestPublicEndpoints:
    def test_services_list_public(self):
        client = APIClient()
        response = client.get('/api/v1/services/services/')
        assert response.status_code == 200

    def test_categories_list_public(self):
        client = APIClient()
        response = client.get('/api/v1/services/service-categories/')
        assert response.status_code == 200

    def test_masters_list_public(self):
        client = APIClient()
        response = client.get('/api/v1/staff/masters/')
        assert response.status_code == 200

    def test_promotions_list_public(self):
        client = APIClient()
        response = client.get('/api/v1/promotions/promotions/')
        assert response.status_code == 200

    def test_reviews_list_public(self):
        client = APIClient()
        response = client.get('/api/v1/reviews/reviews/')
        assert response.status_code == 200

    def test_auth_endpoints_public(self):
        client = APIClient()
        response = client.post('/api/v1/auth/sms/send/', {'phone': '+79001111111'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestAppointmentPermissions:
    def setup_appointment(self):
        user = User.objects.create_user(username='appt_user', password='pass')
        client_obj = Client.objects.create(user=user, phone='+79001111111')
        master_user = User.objects.create_user(username='appt_master', password='pass')
        master = Master.objects.create(user=master_user, phone='+79002222222', is_active=True)
        category = ServiceCategory.objects.create(name='Test', slug='test', icon='t')
        service = Service.objects.create(
            category=category, name='Test', slug='test-svc',
            base_duration_minutes=60, base_price=Decimal('1000.00'),
        )
        future = timezone.now() + timedelta(days=2, hours=3)
        appt = Appointment.objects.create(
            client=client_obj, master=master,
            datetime_start=future, datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        AppointmentService.objects.create(
            appointment=appt, service=service,
            price_at_booking=Decimal('1000.00'), duration_at_booking=60,
        )
        return user, client_obj, appt

    def test_user_can_cancel_own_appointment(self):
        user, _, appt = self.setup_appointment()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(f'/api/v1/appointments/appointments/{appt.id}/cancel/')
        assert response.status_code == 200

    def test_user_cannot_cancel_others_appointment(self):
        user, _, appt = self.setup_appointment()
        other_user = User.objects.create_user(username='other_appt', password='pass')
        client = APIClient()
        client.force_authenticate(user=other_user)
        response = client.post(f'/api/v1/appointments/appointments/{appt.id}/cancel/')
        assert response.status_code == 403

    def test_unauthenticated_cannot_cancel(self):
        _, _, appt = self.setup_appointment()
        client = APIClient()
        response = client.post(f'/api/v1/appointments/appointments/{appt.id}/cancel/')
        assert response.status_code in [401, 403]

    def test_user_can_view_own_appointments(self):
        user, _, appt = self.setup_appointment()
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f'/api/v1/appointments/appointments/{appt.id}/')
        assert response.status_code == 200

    def test_user_cannot_view_others_appointments(self):
        user, _, appt = self.setup_appointment()
        other_user = User.objects.create_user(username='other_view', password='pass')
        client = APIClient()
        client.force_authenticate(user=other_user)
        response = client.get(f'/api/v1/appointments/appointments/{appt.id}/')
        assert response.status_code == 403
