from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient
from apps.clients.models import Client
from apps.services.models import ServiceCategory, Service


class PromotionTests(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.category = ServiceCategory.objects.create(name='Стрижки', slug='haircuts', icon='scissors')
        self.service = Service.objects.create(
            category=self.category,
            name='Стрижка',
            slug='haircut',
            base_duration_minutes=60,
            base_price=1500,
        )

        today = timezone.now().date()
        self.active_promotion = Promotion.objects.create(
            name='Летняя скидка',
            description='Скидка на все услуги летом',
            discount_percent=Decimal('20.00'),
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=10),
        )
        self.active_promotion.applicable_services.add(self.service)

        self.expired_promotion = Promotion.objects.create(
            name='Зимняя скидка',
            description='Скидка на все услуги зимой',
            discount_percent=Decimal('15.00'),
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
        )

        self.future_promotion = Promotion.objects.create(
            name='Осенняя скидка',
            description='Скидка на все услуги осенью',
            discount_percent=Decimal('10.00'),
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=60),
        )

        self.promotions_url = '/api/v1/promotions/promotions/'

    def test_list_only_active_promotions(self):
        response = self.api_client.get(self.promotions_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Летняя скидка')

    def test_active_property(self):
        self.assertTrue(self.active_promotion.is_active)
        self.assertFalse(self.expired_promotion.is_active)
        self.assertFalse(self.future_promotion.is_active)

    def test_retrieve_promotion(self):
        response = self.api_client.get(f'{self.promotions_url}{self.active_promotion.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Летняя скидка')
        self.assertIn(self.service.id, response.data['applicable_services'])


class GiftCertificateTests(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.gift_certificates_url = '/api/v1/promotions/gift-certificates/'

    def test_create_gift_certificate(self):
        response = self.api_client.post(self.gift_certificates_url, {
            'nominal': '5000.00',
            'buyer_name': 'Иван Иванов',
            'recipient_email': 'recipient@example.com',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(GiftCertificate.objects.count(), 1)
        cert = GiftCertificate.objects.first()
        self.assertEqual(len(cert.code), 12)
        self.assertEqual(cert.nominal, Decimal('5000.00'))
        self.assertEqual(cert.buyer_name, 'Иван Иванов')
        self.assertEqual(cert.recipient_email, 'recipient@example.com')
        self.assertFalse(cert.is_used)

    def test_certificate_code_generation(self):
        cert1 = GiftCertificate.objects.create(
            nominal=Decimal('1000.00'),
            buyer_name='Тест1',
            recipient_email='test1@example.com',
        )
        cert2 = GiftCertificate.objects.create(
            nominal=Decimal('2000.00'),
            buyer_name='Тест2',
            recipient_email='test2@example.com',
        )
        self.assertNotEqual(cert1.code, cert2.code)
        self.assertEqual(len(cert1.code), 12)
        self.assertEqual(len(cert2.code), 12)

    def test_list_gift_certificates_requires_admin(self):
        user = User.objects.create_user(username='regularuser', password='testpass123')
        self.api_client.force_authenticate(user=user)
        response = self.api_client.get(self.gift_certificates_url)
        self.assertIn(response.status_code, [401, 403])

    def test_list_gift_certificates_admin(self):
        admin_user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        GiftCertificate.objects.create(
            nominal=Decimal('3000.00'),
            buyer_name='Покупатель',
            recipient_email='recipient@example.com',
        )
        self.api_client.force_authenticate(user=admin_user)
        response = self.api_client.get(self.gift_certificates_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)


class BlacklistedClientTests(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.admin_user = User.objects.create_user(username='admin', password='testpass123', is_staff=True)
        self.regular_user = User.objects.create_user(username='regular', password='testpass123')
        self.client = Client.objects.create(user=self.regular_user, phone='+79005555555')
        self.blacklist_url = '/api/v1/promotions/blacklist/'

    def test_create_blacklist_entry(self):
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.post(self.blacklist_url, {
            'client': self.client.id,
            'reason': 'Систематические опоздания',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(BlacklistedClient.objects.count(), 1)
        self.assertEqual(BlacklistedClient.objects.first().reason, 'Систематические опоздания')

    def test_list_blacklist_requires_admin(self):
        self.api_client.force_authenticate(user=self.regular_user)
        response = self.api_client.get(self.blacklist_url)
        self.assertIn(response.status_code, [401, 403])

    def test_update_blacklist_entry(self):
        entry = BlacklistedClient.objects.create(client=self.client, reason='Старая причина')
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.patch(f'{self.blacklist_url}{entry.id}/', {'reason': 'Новая причина'})
        self.assertEqual(response.status_code, 200)
        entry.refresh_from_db()
        self.assertEqual(entry.reason, 'Новая причина')

    def test_delete_blacklist_entry(self):
        entry = BlacklistedClient.objects.create(client=self.client, reason='Причина')
        self.api_client.force_authenticate(user=self.admin_user)
        response = self.api_client.delete(f'{self.blacklist_url}{entry.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(BlacklistedClient.objects.count(), 0)

    def test_blacklist_str_representation(self):
        entry = BlacklistedClient.objects.create(client=self.client, reason='Длинная причина для проверки обрезки в строковом представлении')
        self.assertIn('+79005555555', str(entry))
        self.assertIn('Длинная причина для проверки обрезки', str(entry))
