from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.clients.models import Client


class AuthAppTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_phone = '+79991234567'
        self.test_password = 'testpass123'

    def test_send_sms_code(self):
        response = self.client.post('/api/v1/auth/sms/send/', {
            'phone': self.test_phone,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.data)
        self.assertEqual(response.data['phone'], self.test_phone)

    def test_verify_sms_code(self):
        send_response = self.client.post('/api/v1/auth/sms/send/', {
            'phone': self.test_phone,
        })
        code = send_response.data['code']

        response = self.client.post('/api/v1/auth/sms/verify/', {
            'phone': self.test_phone,
            'sms_code': code,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['verified'])

    def test_register_with_phone(self):
        send_response = self.client.post('/api/v1/auth/sms/send/', {
            'phone': self.test_phone,
        })
        code = send_response.data['code']

        response = self.client.post('/api/v1/auth/register/', {
            'phone': self.test_phone,
            'password': self.test_password,
            'sms_code': code,
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['phone'], self.test_phone)

        self.assertTrue(User.objects.filter(username=self.test_phone).exists())
        self.assertTrue(Client.objects.filter(phone=self.test_phone).exists())

    def test_login_with_phone(self):
        User.objects.create_user(username=self.test_phone, password=self.test_password)
        Client.objects.create(phone=self.test_phone)

        response = self.client.post('/api/v1/auth/login/', {
            'phone': self.test_phone,
            'password': self.test_password,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(username=self.test_phone, password=self.test_password)
        Client.objects.create(phone=self.test_phone)

        response = self.client.post('/api/v1/auth/login/', {
            'phone': self.test_phone,
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 400)

    def test_register_duplicate_phone(self):
        User.objects.create_user(username=self.test_phone, password=self.test_password)

        response = self.client.post('/api/v1/auth/register/', {
            'phone': self.test_phone,
            'password': 'anotherpass123',
        })
        self.assertEqual(response.status_code, 400)

    def test_profile_requires_auth(self):
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, 401)

    def test_profile_returns_user_data(self):
        user = User.objects.create_user(username=self.test_phone, password=self.test_password)
        Client.objects.create(phone=self.test_phone, user=user)

        self.client.force_authenticate(user=user)
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.test_phone)
        self.assertIn('client', response.data)
        self.assertEqual(response.data['client']['phone'], self.test_phone)
