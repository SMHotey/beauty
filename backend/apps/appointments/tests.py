from datetime import timedelta
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.clients.models import Client
from apps.staff.models import Master, MasterService
from apps.services.models import ServiceCategory, Service
from apps.appointments.models import Appointment, AppointmentService
from apps.appointments.utils import get_available_slots


class GuestBookingTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.master_user = User.objects.create_user(username='master', password='pass123')
        self.master = Master.objects.create(
            user=self.master_user,
            phone='+79001111111',
            is_active=True,
            working_hours={'0': {'start': '09:00', 'end': '18:00'}},
            break_slots=[]
        )
        self.category = ServiceCategory.objects.create(name='Стрижки', slug='haircuts', icon='scissors')
        self.service = Service.objects.create(
            category=self.category,
            name='Стрижка',
            slug='haircut',
            base_duration_minutes=60,
            base_price=Decimal('1500.00'),
        )
        MasterService.objects.create(
            master=self.master,
            service=self.service,
            is_enabled=True
        )
        self.url = '/api/v1/appointments/guest/'

    def test_guest_booking_with_phone(self):
        future_time = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'phone': '+79009999999',
            'name': 'Иван',
            'master_id': self.master.id,
            'service_ids': [self.service.id],
            'datetime_start': future_time.isoformat(),
        }
        response = self.client_api.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertTrue(Client.objects.filter(phone='+79009999999').exists())

    def test_guest_booking_without_phone(self):
        future_time = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': self.master.id,
            'service_ids': [self.service.id],
            'datetime_start': future_time.isoformat(),
        }
        response = self.client_api.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Appointment.objects.count(), 1)
        appt = Appointment.objects.first()
        self.assertIsNone(appt.client)

    def test_guest_booking_past_time(self):
        past_time = timezone.now() - timedelta(hours=1)
        data = {
            'master': self.master.id,
            'service_ids': [self.service.id],
            'datetime_start': past_time.isoformat(),
        }
        response = self.client_api.post(self.url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_guest_booking_conflict(self):
        future_time = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': self.master.id,
            'service_ids': [self.service.id],
            'datetime_start': future_time.isoformat(),
        }
        response1 = self.client_api.post(self.url, data, format='json')
        self.assertEqual(response1.status_code, 201)
        response2 = self.client_api.post(self.url, data, format='json')
        self.assertEqual(response2.status_code, 400)


class SlotGenerationTests(TestCase):
    def setUp(self):
        self.master_user = User.objects.create_user(username='master', password='pass123')
        # Set working_hours for ALL days to avoid weekday mismatch
        self.working_hours = {str(i): {'start': '09:00', 'end': '12:00'} for i in range(7)}
        self.master = Master.objects.create(
            user=self.master_user,
            phone='+79001111111',
            is_active=True,
            working_hours=self.working_hours,
            break_slots=[]
        )
        self.category = ServiceCategory.objects.create(name='Стрижки', slug='haircuts', icon='scissors')
        self.service = Service.objects.create(
            category=self.category,
            name='Стрижка',
            slug='haircut',
            base_duration_minutes=60,
            base_price=Decimal('1500.00'),
        )
        MasterService.objects.create(
            master=self.master,
            service=self.service,
            is_enabled=True
        )
        self.future_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    def test_available_slots_generated(self):
        slots = get_available_slots(self.master.id, self.future_date, [self.service.id])
        self.assertTrue(len(slots) > 0)

    def test_no_slots_for_non_working_day(self):
        # Clear working hours for the specific weekday
        from datetime import datetime
        target_date = datetime.strptime(self.future_date, '%Y-%m-%d').date()
        weekday = str(target_date.weekday())
        self.master.working_hours = {}
        self.master.save()
        slots = get_available_slots(self.master.id, self.future_date, [self.service.id])
        self.assertEqual(slots, [])

    def test_no_slots_for_nonexistent_master(self):
        slots = get_available_slots(99999, self.future_date, [self.service.id])
        self.assertEqual(slots, [])


class CancellationTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client.objects.create(user=self.user, phone='+79001234567')
        self.master_user = User.objects.create_user(username='master', password='pass123')
        self.master = Master.objects.create(
            user=self.master_user,
            phone='+79001111111',
            is_active=True,
            working_hours={'0': {'start': '09:00', 'end': '18:00'}},
            break_slots=[]
        )
        self.category = ServiceCategory.objects.create(name='Стрижки', slug='haircuts', icon='scissors')
        self.service = Service.objects.create(
            category=self.category,
            name='Стрижка',
            slug='haircut',
            base_duration_minutes=60,
            base_price=Decimal('1500.00'),
        )
        self.future_time = timezone.now() + timedelta(days=2, hours=3)
        self.appointment = Appointment.objects.create(
            client=self.client,
            master=self.master,
            datetime_start=self.future_time,
            datetime_end=self.future_time + timedelta(hours=1),
            status='pending',
        )
        AppointmentService.objects.create(
            appointment=self.appointment,
            service=self.service,
            price_at_booking=Decimal('1500.00'),
            duration_at_booking=60,
        )
        self.client_api.force_authenticate(user=self.user)

    def test_cancel_appointment(self):
        url = f'/api/v1/appointments/appointments/{self.appointment.id}/'
        response = self.client_api.post(f'{url}cancel/')
        self.assertEqual(response.status_code, 200)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'cancelled_by_client')

    def test_cancel_already_cancelled(self):
        self.appointment.status = 'cancelled_by_client'
        self.appointment.save()
        url = f'/api/v1/appointments/appointments/{self.appointment.id}/'
        response = self.client_api.post(f'{url}cancel/')
        self.assertEqual(response.status_code, 400)

    def test_cancel_too_late(self):
        self.appointment.datetime_start = timezone.now() + timedelta(hours=1)
        self.appointment.save()
        url = f'/api/v1/appointments/appointments/{self.appointment.id}/'
        response = self.client_api.post(f'{url}cancel/')
        self.assertEqual(response.status_code, 400)

    def test_cancel_other_user_appointment(self):
        other_user = User.objects.create_user(username='other', password='pass123')
        self.client_api.force_authenticate(user=other_user)
        url = f'/api/v1/appointments/appointments/{self.appointment.id}/'
        response = self.client_api.post(f'{url}cancel/')
        self.assertEqual(response.status_code, 403)
