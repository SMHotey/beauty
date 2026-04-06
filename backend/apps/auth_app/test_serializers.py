from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from apps.auth_app.serializers import PhoneRegisterSerializer, PhoneLoginSerializer, SmsVerifySerializer
from apps.clients.models import Client


@pytest.mark.django_db
class TestPhoneRegisterSerializer:
    def test_valid_registration(self):
        from apps.auth_app.sms_service import SMSService
        phone = '+79001111111'
        code = SMSService.send_code(phone)

        serializer = PhoneRegisterSerializer(data={
            'phone': phone,
            'password': 'testpass123',
            'sms_code': code,
        })
        assert serializer.is_valid(), serializer.errors

    def test_duplicate_phone_rejected(self):
        User.objects.create_user(username='+79001111111', password='pass')
        serializer = PhoneRegisterSerializer(data={
            'phone': '+79001111111',
            'password': 'testpass123',
        })
        assert not serializer.is_valid()
        assert 'phone' in serializer.errors

    def test_short_password_rejected(self):
        serializer = PhoneRegisterSerializer(data={
            'phone': '+79001111111',
            'password': '123',
        })
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_creates_user_and_client(self):
        from apps.auth_app.sms_service import SMSService
        phone = '+79002222222'
        code = SMSService.send_code(phone)

        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.post('/register', {'phone': phone, 'password': 'pass123', 'sms_code': code})

        serializer = PhoneRegisterSerializer(data={
            'phone': phone,
            'password': 'pass123',
            'sms_code': code,
        }, context={'request': request})
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()
        assert User.objects.filter(username=phone).exists()
        assert Client.objects.filter(phone=phone).exists()

    def test_referral_code(self):
        from apps.auth_app.sms_service import SMSService
        referrer = Client.objects.create(phone='+79003333333')
        phone = '+79004444444'
        code = SMSService.send_code(phone)

        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.post('/register', {
            'phone': phone, 'password': 'pass123', 'sms_code': code,
            'referral_code': referrer.referral_code,
        })

        serializer = PhoneRegisterSerializer(data={
            'phone': phone,
            'password': 'pass123',
            'sms_code': code,
        }, context={'request': request})
        assert serializer.is_valid(), serializer.errors

        user = serializer.save()
        client = Client.objects.get(user=user)
        assert client.referred_by == referrer


@pytest.mark.django_db
class TestPhoneLoginSerializer:
    def test_valid_login(self):
        phone = '+79005555555'
        User.objects.create_user(username=phone, password='pass123')
        Client.objects.create(phone=phone)

        serializer = PhoneLoginSerializer(data={
            'phone': phone,
            'password': 'pass123',
        })
        assert serializer.is_valid(), serializer.errors
        assert 'user' in serializer.validated_data

    def test_wrong_password(self):
        phone = '+79006666666'
        User.objects.create_user(username=phone, password='pass123')
        Client.objects.create(phone=phone)

        serializer = PhoneLoginSerializer(data={
            'phone': phone,
            'password': 'wrongpass',
        })
        assert not serializer.is_valid()

    def test_nonexistent_user(self):
        serializer = PhoneLoginSerializer(data={
            'phone': '+79007777777',
            'password': 'pass123',
        })
        assert not serializer.is_valid()

    def test_inactive_user(self):
        phone = '+79008888888'
        user = User.objects.create_user(username=phone, password='pass123', is_active=False)
        Client.objects.create(phone=phone)

        serializer = PhoneLoginSerializer(data={
            'phone': phone,
            'password': 'pass123',
        })
        assert not serializer.is_valid()

    def test_phone_format_normalization(self):
        phone = '+79009999999'
        User.objects.create_user(username=phone, password='pass123')
        Client.objects.create(phone=phone)

        serializer = PhoneLoginSerializer(data={
            'phone': '89009999999',
            'password': 'pass123',
        })
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data['phone'] == phone


@pytest.mark.django_db
class TestSmsVerifySerializer:
    def test_valid_verification(self):
        from apps.auth_app.sms_service import SMSService
        phone = '+79001111111'
        code = SMSService.send_code(phone)

        serializer = SmsVerifySerializer(data={
            'phone': phone,
            'sms_code': code,
        })
        assert serializer.is_valid(), serializer.errors

    def test_invalid_code(self):
        from apps.auth_app.sms_service import SMSService
        phone = '+79002222222'
        SMSService.send_code(phone)

        serializer = SmsVerifySerializer(data={
            'phone': phone,
            'sms_code': '000000',
        })
        assert not serializer.is_valid()

    def test_no_code_sent(self):
        serializer = SmsVerifySerializer(data={
            'phone': '+79003333333',
            'sms_code': '123456',
        })
        assert not serializer.is_valid()
