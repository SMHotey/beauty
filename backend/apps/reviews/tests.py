from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from apps.clients.models import Client
from apps.staff.models import Master
from apps.services.models import ServiceCategory, Service
from apps.appointments.models import Appointment
from apps.reviews.models import Review


class ReviewCreationTests(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.user = User.objects.create_user(username='clientuser', password='testpass123')
        self.client = Client.objects.create(user=self.user, phone='+79001111111')

        self.master_user = User.objects.create_user(username='masteruser', password='testpass123')
        self.master = Master.objects.create(user=self.master_user, phone='+79002222222', is_active=True)

        self.category = ServiceCategory.objects.create(name='Стрижки', slug='haircuts', icon='scissors')
        self.service = Service.objects.create(
            category=self.category,
            name='Стрижка женская',
            slug='womens-haircut',
            base_duration_minutes=60,
            base_price=1500,
        )

        self.completed_appointment = Appointment.objects.create(
            client=self.client,
            master=self.master,
            datetime_start=timezone.now() - timedelta(days=2),
            datetime_end=timezone.now() - timedelta(days=2, hours=-1),
            status='completed',
        )

        self.pending_appointment = Appointment.objects.create(
            client=self.client,
            master=self.master,
            datetime_start=timezone.now() + timedelta(days=1),
            datetime_end=timezone.now() + timedelta(days=1, hours=1),
            status='pending',
        )

        self.review_url = '/api/v1/reviews/reviews/'

    def test_create_review_for_completed_appointment(self):
        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.post(self.review_url, {
            'appointment': self.completed_appointment.id,
            'rating': 5,
            'comment': 'Отличная стрижка!',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.first().rating, 5)

    def test_cannot_create_review_for_non_completed_appointment(self):
        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.post(self.review_url, {
            'appointment': self.pending_appointment.id,
            'rating': 4,
            'comment': 'Ещё не было записи.',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_cannot_create_review_for_others_appointment(self):
        other_user = User.objects.create_user(username='otheruser', password='testpass123')
        other_client = Client.objects.create(user=other_user, phone='+79003333333')
        other_appointment = Appointment.objects.create(
            client=other_client,
            master=self.master,
            datetime_start=timezone.now() - timedelta(days=1),
            datetime_end=timezone.now() - timedelta(days=1, hours=-1),
            status='completed',
        )

        self.api_client.force_authenticate(user=self.user)
        response = self.api_client.post(self.review_url, {
            'appointment': other_appointment.id,
            'rating': 5,
            'comment': 'Не моя запись.',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_cannot_create_duplicate_review(self):
        self.api_client.force_authenticate(user=self.user)
        self.api_client.post(self.review_url, {
            'appointment': self.completed_appointment.id,
            'rating': 5,
            'comment': 'Первый отзыв.',
        })
        response = self.api_client.post(self.review_url, {
            'appointment': self.completed_appointment.id,
            'rating': 4,
            'comment': 'Второй отзыв.',
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 1)

    def test_list_reviews_public(self):
        Review.objects.create(
            client=self.client,
            appointment=self.completed_appointment,
            rating=5,
            comment='Супер!',
        )
        response = self.api_client.get(self.review_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_reviews_by_master(self):
        other_master_user = User.objects.create_user(username='othermaster', password='testpass123')
        other_master = Master.objects.create(user=other_master_user, phone='+79004444444', is_active=True)

        other_appointment = Appointment.objects.create(
            client=self.client,
            master=other_master,
            datetime_start=timezone.now() - timedelta(days=3),
            datetime_end=timezone.now() - timedelta(days=3, hours=-1),
            status='completed',
        )

        Review.objects.create(client=self.client, appointment=self.completed_appointment, rating=5, comment='Мастер 1')
        Review.objects.create(client=self.client, appointment=other_appointment, rating=4, comment='Мастер 2')

        response = self.api_client.get(f'{self.review_url}?master_id={self.master.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['master_name'], self.master.user.get_full_name())
