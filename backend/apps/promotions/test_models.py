from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient, Setting


@pytest.mark.django_db
class TestPromotionModel:
    def test_str(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Test Promo',
            description='Description',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
        )
        assert str(promo) == 'Test Promo'

    def test_is_active_current(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Active', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
        )
        assert promo.is_active is True

    def test_is_active_expired(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Expired', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=30),
            end_date=today - timedelta(days=10),
        )
        assert promo.is_active is False

    def test_is_active_not_started(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Future', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=30),
        )
        assert promo.is_active is False

    def test_is_active_start_date_today(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Starts Today', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today,
            end_date=today + timedelta(days=10),
        )
        assert promo.is_active is True

    def test_is_active_end_date_today(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Ends Today', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=10),
            end_date=today,
        )
        assert promo.is_active is True

    def test_m2m_services(self, service):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='Promo', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
        )
        promo.applicable_services.add(service)
        assert promo.applicable_services.filter(id=service.id).exists()

    def test_optional_promo_code(self):
        today = timezone.now().date()
        promo = Promotion.objects.create(
            name='No Code', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
        )
        assert promo.promo_code is None

    def test_ordering(self):
        today = timezone.now().date()
        p1 = Promotion.objects.create(
            name='Older', description='Desc',
            discount_percent=Decimal('10.00'),
            start_date=today - timedelta(days=20),
            end_date=today + timedelta(days=10),
        )
        p2 = Promotion.objects.create(
            name='Newer', description='Desc',
            discount_percent=Decimal('15.00'),
            start_date=today - timedelta(days=5),
            end_date=today + timedelta(days=15),
        )
        promos = list(Promotion.objects.all())
        assert promos[0] == p2
        assert promos[1] == p1


@pytest.mark.django_db
class TestGiftCertificateModel:
    def test_str(self):
        cert = GiftCertificate.objects.create(
            nominal=Decimal('5000.00'),
            buyer_name='Buyer',
            recipient_email='test@example.com',
        )
        assert '5000.00' in str(cert)

    def test_auto_code_generation(self):
        cert = GiftCertificate.objects.create(
            nominal=Decimal('1000.00'),
            buyer_name='Buyer',
            recipient_email='test@example.com',
        )
        assert cert.code is not None
        assert len(cert.code) == 12
        assert cert.code == cert.code.upper()

    def test_code_unique(self):
        codes = set()
        for i in range(10):
            cert = GiftCertificate.objects.create(
                nominal=Decimal(f'{i+1}000.00'),
                buyer_name=f'Buyer{i}',
                recipient_email=f'test{i}@example.com',
            )
            codes.add(cert.code)
        assert len(codes) == 10

    def test_is_used_default(self):
        cert = GiftCertificate.objects.create(
            nominal=Decimal('1000.00'),
            buyer_name='Buyer',
            recipient_email='test@example.com',
        )
        assert cert.is_used is False
        assert cert.used_at is None

    def test_mark_as_used(self):
        cert = GiftCertificate.objects.create(
            nominal=Decimal('1000.00'),
            buyer_name='Buyer',
            recipient_email='test@example.com',
        )
        cert.is_used = True
        cert.used_at = timezone.now()
        cert.save()
        cert.refresh_from_db()
        assert cert.is_used is True
        assert cert.used_at is not None


@pytest.mark.django_db
class TestBlacklistedClientModel:
    def test_str_short_reason(self, client):
        entry = BlacklistedClient.objects.create(client=client, reason='Short reason')
        assert client.phone in str(entry)
        assert 'Short reason' in str(entry)

    def test_str_long_reason_truncated(self, client):
        long_reason = 'A' * 100
        entry = BlacklistedClient.objects.create(client=client, reason=long_reason)
        assert client.phone in str(entry)
        assert len(str(entry)) < len(long_reason) + len(client.phone) + 10

    def test_one_to_one_client(self, client):
        entry = BlacklistedClient.objects.create(client=client, reason='Test')
        assert client.blacklist_entry == entry

    def test_cascade_delete(self, client):
        entry = BlacklistedClient.objects.create(client=client, reason='Test')
        client.delete()
        assert not BlacklistedClient.objects.filter(id=entry.id).exists()


@pytest.mark.django_db
class TestSettingModel:
    def test_str(self):
        setting = Setting.objects.create(key='TEST_KEY', value='test_value')
        assert str(setting) == 'TEST_KEY = test_value'

    def test_key_unique(self):
        Setting.objects.create(key='UNIQUE_KEY', value='val1')
        with pytest.raises(Exception):
            Setting.objects.create(key='UNIQUE_KEY', value='val2')

    def test_value_can_be_any_text(self):
        setting = Setting.objects.create(key='JSON_KEY', value='{"nested": "value"}')
        assert setting.value == '{"nested": "value"}'
