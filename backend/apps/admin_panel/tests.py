from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from apps.staff.models import Master
from apps.clients.models import Client
from apps.services.models import ServiceCategory, Service
from apps.appointments.models import Appointment, AppointmentService


class AdminPanelTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@test.com',
        )
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpass123',
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass123',
        )

        self.master_user = User.objects.create_user(
            username='+79991111111',
            first_name='Иван',
            last_name='Мастеров',
        )
        self.master = Master.objects.create(
            user=self.master_user,
            phone='+79991111111',
            is_active=True,
        )

        self.category = ServiceCategory.objects.create(
            name='Стрижки',
            slug='haircuts',
            icon='scissors',
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Женская стрижка',
            slug='womens-haircut',
            base_duration_minutes=60,
            base_price=1500,
        )

        self.client_profile = Client.objects.create(
            phone='+79992222222',
            user=self.regular_user,
        )

        now = timezone.now()
        self.appointment = Appointment.objects.create(
            client=self.client_profile,
            master=self.master,
            datetime_start=now + timedelta(days=1),
            datetime_end=now + timedelta(days=1, hours=1),
            status='completed',
            total_price=Decimal('1500'),
        )
        AppointmentService.objects.create(
            appointment=self.appointment,
            service=self.service,
            price_at_booking=Decimal('1500'),
            duration_at_booking=60,
        )

    def test_dashboard_stats_requires_admin(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/v1/admin-panel/dashboard/stats/')
        self.assertEqual(response.status_code, 403)

    def test_dashboard_stats_returns_data(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/admin-panel/dashboard/stats/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('revenue', response.data)
        self.assertIn('appointments_count', response.data)
        self.assertIn('masters_count', response.data)
        self.assertGreaterEqual(response.data['masters_count'], 1)

    def test_admin_calendar_returns_data(self):
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        response = self.client.get('/api/v1/admin-panel/calendar/', {
            'month': now.month,
            'year': now.year,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_admin_calendar_filter_by_master(self):
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        response = self.client.get('/api/v1/admin-panel/calendar/', {
            'month': now.month,
            'year': now.year,
            'master_id': self.master.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['master_id'], self.master.id)

    def test_sales_report_json(self):
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        response = self.client.get('/api/v1/admin-panel/reports/sales/', {
            'date_from': (now - timedelta(days=7)).isoformat(),
            'date_to': (now + timedelta(days=7)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_sales_report_xlsx(self):
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        # DRF APIClient intercepts 'format' kwarg, so we call the view directly
        from rest_framework.test import APIRequestFactory
        from apps.admin_panel.views import SalesReportView
        factory = APIRequestFactory()
        request = factory.get(
            '/api/v1/admin-panel/reports/sales/',
            data={
                'date_from': (now - timedelta(days=7)).isoformat(),
                'date_to': (now + timedelta(days=7)).isoformat(),
                'format': 'xlsx',
            },
        )
        request.user = self.admin_user
        view = SalesReportView.as_view()
        response = view(request)
        response.render()
        self.assertEqual(response.status_code, 200, f"Got {response.status_code}")
        self.assertEqual(
            response['Content-Disposition'].split(';')[0].strip(),
            'attachment',
        )
        self.assertIn('xlsx', response['Content-Disposition'])

    def test_admin_master_list_requires_auth(self):
        response = self.client.get('/api/v1/admin-panel/masters/')
        self.assertEqual(response.status_code, 401)

    def test_admin_master_list_returns_data(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/admin-panel/masters/')
        self.assertEqual(response.status_code, 200)

    def test_admin_appointment_list(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/v1/admin-panel/appointments/')
        self.assertEqual(response.status_code, 200)

    def test_admin_appointment_create(self):
        self.client.force_authenticate(user=self.admin_user)
        now = timezone.now()
        response = self.client.post('/api/v1/admin-panel/appointments/', {
            'master_id': self.master.id,
            'client_phone': '+79993333333',
            'service_ids': [self.service.id],
            'datetime_start': (now + timedelta(days=2)).isoformat(),
            'datetime_end': (now + timedelta(days=2, hours=1)).isoformat(),
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.data)

    def test_admin_appointment_status_update(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(
            f'/api/v1/admin-panel/appointments/{self.appointment.id}/',
            {'status': 'cancelled_by_admin'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'cancelled_by_admin')

    def test_sms_broadcast_requires_admin(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post('/api/v1/admin-panel/sms-broadcast/', {
            'message': 'Тестовая рассылка',
            'send_to_all': True,
        })
        self.assertEqual(response.status_code, 403)

    def test_sms_broadcast_send_to_all(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/v1/admin-panel/sms-broadcast/', {
            'message': 'Тестовая рассылка',
            'send_to_all': True,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('phones_count', response.data)
