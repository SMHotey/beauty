from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.clients.models import Client, FavoriteMaster
from apps.staff.models import Master
from apps.services.models import ServiceCategory, Service


class ClientProfileTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client.objects.create(user=self.user, phone='+79001234567')

    def test_get_profile(self):
        self.client_api.force_authenticate(user=self.user)
        response = self.client_api.get('/api/v1/clients/profile/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['phone'], '+79001234567')

    def test_get_profile_unauthenticated(self):
        response = self.client_api.get('/api/v1/clients/profile/me/')
        self.assertIn(response.status_code, [401, 403])

    def test_update_profile(self):
        self.client_api.force_authenticate(user=self.user)
        response = self.client_api.patch('/api/v1/clients/profile/update_me/', {'phone': '+79009876543'})
        self.assertEqual(response.status_code, 200)
        self.client.refresh_from_db()
        self.assertEqual(self.client.phone, '+79009876543')


class FavoriteMasterTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.master_user = User.objects.create_user(username='masteruser', password='testpass123')
        self.client = Client.objects.create(user=self.user, phone='+79001234567')
        self.master = Master.objects.create(user=self.master_user, phone='+79007654321', is_active=True)
        self.favorite_url = '/api/v1/clients/favorites/'

    def test_list_favorites_empty(self):
        self.client_api.force_authenticate(user=self.user)
        response = self.client_api.get(self.favorite_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)

    def test_add_favorite(self):
        self.client_api.force_authenticate(user=self.user)
        response = self.client_api.post(self.favorite_url, {'master': self.master.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FavoriteMaster.objects.count(), 1)

    def test_remove_favorite(self):
        self.client_api.force_authenticate(user=self.user)
        fav = FavoriteMaster.objects.create(client=self.client, master=self.master)
        response = self.client_api.delete(f'{self.favorite_url}{fav.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(FavoriteMaster.objects.count(), 0)

    def test_duplicate_favorite(self):
        self.client_api.force_authenticate(user=self.user)
        self.client_api.post(self.favorite_url, {'master': self.master.id})
        response = self.client_api.post(self.favorite_url, {'master': self.master.id})
        self.assertIn(response.status_code, [400, 403])
