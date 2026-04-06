from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentService
from apps.appointments.serializers import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentServiceSerializer,
    GuestAppointmentSerializer,
)
from apps.clients.models import Client
from apps.services.models import Service, ServiceCategory
from apps.staff.models import Master, MasterService


@pytest.mark.django_db
class TestAppointmentServiceSerializer:
    def test_serializes_appointment_service(self, appointment):
        appt_service = appointment.services.first()
        serializer = AppointmentServiceSerializer(appt_service)
        assert serializer.data['service_name'] == 'Haircut'
        assert serializer.data['price_at_booking'] == '1500.00'
        assert serializer.data['duration_at_booking'] == 60

    def test_read_only_fields(self, appointment):
        appt_service = appointment.services.first()
        serializer = AppointmentServiceSerializer(appt_service)
        assert 'id' in serializer.data
        assert 'service_name' in serializer.data


@pytest.mark.django_db
class TestAppointmentSerializer:
    def test_serializes_appointment(self, appointment):
        serializer = AppointmentSerializer(appointment)
        assert serializer.data['master_name'] == 'Иван Петров'
        assert serializer.data['status'] == 'pending'
        assert serializer.data['total_price'] == '1500.00'
        assert len(serializer.data['services']) == 1

    def test_read_only_fields(self, appointment):
        serializer = AppointmentSerializer(appointment)
        assert 'id' in serializer.data
        assert 'created_at' in serializer.data
        assert 'master_name' in serializer.data

    def test_guest_appointment_has_no_client_name(self, master, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        appt = Appointment.objects.create(
            client=None,
            master=master,
            datetime_start=future,
            datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        serializer = AppointmentSerializer(appt)
        assert serializer.data['client'] is None


@pytest.mark.django_db
class TestGuestAppointmentSerializer:
    def test_valid_data(self, master, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'phone': '+79001111111',
            'name': 'Test',
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_invalid_past_time(self, master, service):
        past = timezone.now() - timedelta(hours=1)
        data = {
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': past.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'datetime_start' in serializer.errors

    def test_invalid_master(self, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': 99999,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'master_id' in serializer.errors

    def test_inactive_master_rejected(self, service):
        inactive_user = User.objects.create_user(username='inactive', password='pass')
        inactive_master = Master.objects.create(
            user=inactive_user,
            phone='+79007777777',
            is_active=False,
        )
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': inactive_master.id,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert not serializer.is_valid()

    def test_conflicting_time_rejected(self, master, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        Appointment.objects.create(
            client=None,
            master=master,
            datetime_start=future,
            datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        data = {
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert not serializer.is_valid()
        assert 'datetime_start' in serializer.errors

    def test_empty_service_ids_rejected(self, master):
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': master.id,
            'service_ids': [],
            'datetime_start': future.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert not serializer.is_valid()

    def test_validates_master_exists(self, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': 99999,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = GuestAppointmentSerializer(data=data)
        assert not serializer.is_valid()


@pytest.mark.django_db
class TestAppointmentCreateSerializer:
    def test_valid_data(self, client, master, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = AppointmentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_with_bonuses(self, client, master, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
            'use_bonuses': True,
        }
        serializer = AppointmentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['use_bonuses'] is True

    def test_invalid_past_time(self, client, master, service):
        past = timezone.now() - timedelta(hours=1)
        data = {
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': past.isoformat(),
        }
        serializer = AppointmentCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_conflict_detection(self, client, master, service):
        future = timezone.now() + timedelta(days=1, hours=2)
        Appointment.objects.create(
            client=client,
            master=master,
            datetime_start=future,
            datetime_end=future + timedelta(hours=1),
            status='pending',
        )
        data = {
            'master_id': master.id,
            'service_ids': [service.id],
            'datetime_start': future.isoformat(),
        }
        serializer = AppointmentCreateSerializer(data=data)
        assert not serializer.is_valid()

    def test_multiple_services_duration(self, client, master, service, service2):
        MasterService.objects.create(master=master, service=service2, is_enabled=True)
        future = timezone.now() + timedelta(days=1, hours=2)
        data = {
            'master_id': master.id,
            'service_ids': [service.id, service2.id],
            'datetime_start': future.isoformat(),
        }
        serializer = AppointmentCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
