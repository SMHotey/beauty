from django.test import TestCase
from rest_framework.test import APIClient
from apps.services.models import ServiceCategory, Service


class ServiceCategoryTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = ServiceCategory.objects.create(
            name='Hair',
            slug='hair',
            icon='scissors',
            order=1,
        )

    def test_category_list_returns_200(self):
        response = self.client.get('/api/v1/services/service-categories/')
        self.assertEqual(response.status_code, 200)

    def test_category_retrieve_returns_200(self):
        response = self.client.get(f'/api/v1/services/service-categories/{self.category.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Hair')


class ServiceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = ServiceCategory.objects.create(
            name='Hair',
            slug='hair',
            icon='scissors',
            order=1,
        )
        self.category2 = ServiceCategory.objects.create(
            name='Nails',
            slug='nails',
            icon='hand',
            order=2,
        )
        self.service1 = Service.objects.create(
            category=self.category,
            name='Haircut',
            slug='haircut',
            base_duration_minutes=30,
            base_price=1500.00,
            gender_target='female',
            is_active=True,
        )
        self.service2 = Service.objects.create(
            category=self.category2,
            name='Manicure',
            slug='manicure',
            base_duration_minutes=60,
            base_price=2000.00,
            gender_target='female',
            is_active=True,
        )

    def test_service_list_returns_200(self):
        response = self.client.get('/api/v1/services/services/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_service_filtering_by_category(self):
        response = self.client.get(f'/api/v1/services/services/?category={self.category.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Haircut')

    def test_service_filtering_by_gender_target(self):
        response = self.client.get('/api/v1/services/services/?gender_target=female')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_service_search(self):
        response = self.client.get('/api/v1/services/services/?search=Haircut')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_inactive_service_not_shown(self):
        Service.objects.create(
            category=self.category,
            name='Inactive Service',
            slug='inactive-service',
            base_duration_minutes=30,
            base_price=1000.00,
            gender_target='unisex',
            is_active=False,
        )
        response = self.client.get('/api/v1/services/services/')
        self.assertEqual(response.data['count'], 2)
