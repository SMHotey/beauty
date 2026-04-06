from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from apps.appointments.models import Appointment, AppointmentService
from apps.clients.models import Client
from apps.services.models import Service, ServiceCategory
from apps.staff.models import Master, MasterService


@pytest.mark.django_db
class TestServiceCategoryModel:
    def test_str(self):
        cat = ServiceCategory.objects.create(name='Hair', slug='hair', icon='scissors', order=1)
        assert str(cat) == 'Hair'

    def test_unique_slug(self):
        ServiceCategory.objects.create(name='Hair', slug='hair', icon='scissors', order=1)
        with pytest.raises(Exception):
            ServiceCategory.objects.create(name='Hair2', slug='hair', icon='scissors2', order=2)

    def test_unique_name(self):
        ServiceCategory.objects.create(name='Hair', slug='hair', icon='scissors', order=1)
        with pytest.raises(Exception):
            ServiceCategory.objects.create(name='Hair', slug='hair2', icon='scissors2', order=2)

    def test_ordering(self):
        cat2 = ServiceCategory.objects.create(name='Zebra', slug='zebra', icon='z', order=10)
        cat1 = ServiceCategory.objects.create(name='Alpha', slug='alpha', icon='a', order=1)
        cats = list(ServiceCategory.objects.all())
        assert cats[0] == cat1
        assert cats[1] == cat2

    def test_default_order(self):
        cat = ServiceCategory.objects.create(name='Test', slug='test', icon='t')
        assert cat.order == 0


@pytest.mark.django_db
class TestServiceModel:
    def test_str(self, category, service):
        assert str(service) == 'Hair — Haircut'

    def test_create_service(self, category):
        s = Service.objects.create(
            category=category,
            name='Test Service',
            slug='test-service',
            base_duration_minutes=45,
            base_price=Decimal('1000.00'),
            gender_target='unisex',
        )
        assert s.name == 'Test Service'
        assert s.base_price == Decimal('1000.00')
        assert s.is_active is True

    def test_inactive_service(self, category):
        s = Service.objects.create(
            category=category,
            name='Inactive',
            slug='inactive',
            base_duration_minutes=30,
            base_price=Decimal('500.00'),
            is_active=False,
        )
        assert s.is_active is False

    def test_gender_choices(self, category):
        for gender in ['female', 'male', 'unisex', 'children']:
            s = Service.objects.create(
                category=category,
                name=f'{gender} service',
                slug=f'{gender}-svc',
                base_duration_minutes=30,
                base_price=Decimal('100.00'),
                gender_target=gender,
            )
            assert s.gender_target == gender

    def test_unique_slug(self, category):
        Service.objects.create(
            category=category,
            name='Unique',
            slug='unique-slug',
            base_duration_minutes=30,
            base_price=Decimal('100.00'),
        )
        with pytest.raises(Exception):
            Service.objects.create(
                category=category,
                name='Unique2',
                slug='unique-slug',
                base_duration_minutes=30,
                base_price=Decimal('200.00'),
            )

    def test_category_relationship(self, category, service):
        assert service.category == category
        assert category.services.filter(id=service.id).exists()
