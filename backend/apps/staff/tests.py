from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from apps.services.models import ServiceCategory, Service
from apps.staff.models import Master, MasterService


class MasterTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='master1',
            first_name='Иван',
            last_name='Петров',
            email='ivan@example.com',
        )
        self.category = ServiceCategory.objects.create(
            name='Hair',
            slug='hair',
            icon='scissors',
            order=1,
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Haircut',
            slug='haircut',
            base_duration_minutes=30,
            base_price=1500.00,
            gender_target='female',
            is_active=True,
        )
        self.master = Master.objects.create(
            user=self.user,
            phone='+79001234567',
            bio='Опытный мастер',
            is_active=True,
            working_hours={'monday': {'start': '09:00', 'end': '18:00'}},
            break_slots=[],
            vacations=[],
        )
        MasterService.objects.create(
            master=self.master,
            service=self.service,
            is_enabled=True,
        )

    def test_master_list_returns_200(self):
        response = self.client.get('/api/v1/staff/masters/')
        self.assertEqual(response.status_code, 200)

    def test_master_list_count(self):
        response = self.client.get('/api/v1/staff/masters/')
        self.assertEqual(response.data['count'], 1)

    def test_master_detail_returns_200(self):
        response = self.client.get(f'/api/v1/staff/masters/{self.master.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['full_name'], 'Иван Петров')

    def test_master_detail_includes_services(self):
        response = self.client.get(f'/api/v1/staff/masters/{self.master.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['services']), 1)

    def test_inactive_master_not_in_list(self):
        inactive_user = User.objects.create_user(
            username='inactive_master',
            first_name='Inactive',
            last_name='Master',
        )
        Master.objects.create(
            user=inactive_user,
            phone='+79009999999',
            is_active=False,
        )
        response = self.client.get('/api/v1/staff/masters/')
        self.assertEqual(response.data['count'], 1)

    def test_master_search(self):
        response = self.client.get('/api/v1/staff/masters/?search=Иван')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
