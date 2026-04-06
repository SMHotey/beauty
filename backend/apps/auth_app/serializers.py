from rest_framework import serializers
from django.contrib.auth.models import User
from apps.clients.models import Client


class PhoneRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, min_length=6)
    sms_code = serializers.CharField(max_length=6, required=False, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)

    def validate_phone(self, value):
        cleaned = value.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned.lstrip('8')
        if User.objects.filter(username=cleaned).exists():
            raise serializers.ValidationError('Пользователь с таким номером телефона уже зарегистрирован.')
        return cleaned

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError('Пароль должен содержать минимум 6 символов.')
        return value

    def validate_sms_code(self, value):
        phone = self.initial_data.get('phone', '')
        from apps.auth_app.sms_service import SMSService
        if not SMSService.verify_code(phone, value):
            raise serializers.ValidationError('Неверный или просроченный код подтверждения.')
        return value

    def create(self, validated_data):
        phone = validated_data['phone']
        password = validated_data['password']
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        validated_data.pop('sms_code', None)

        user = User.objects.create_user(
            username=phone,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        client_data = {'user': user, 'phone': phone}
        request = self.context.get('request')
        if request:
            # DRF Request has .data, WSGIRequest has .POST / .body
            referral_code = getattr(request, 'data', request.POST).get('referral_code')
            if referral_code:
                referred_by = Client.objects.filter(referral_code=referral_code).first()
                if referred_by:
                    client_data['referred_by'] = referred_by

        client = Client.objects.create(**client_data)
        return user


class PhoneLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        raw_input = attrs['phone'].strip()
        from django.contrib.auth import authenticate
        from django.contrib.auth.models import User
        user = None

        if '@' in raw_input:
            user_obj = User.objects.filter(email=raw_input).first()
            if user_obj:
                user = authenticate(username=user_obj.username, password=attrs['password'])
        else:
            phone = raw_input.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone.startswith('+'):
                if phone.startswith('8') and len(phone) == 11:
                    phone = '+7' + phone[1:]
                elif not phone.startswith('7'):
                    phone = '+7' + phone
                else:
                    phone = '+' + phone
            user = authenticate(username=phone, password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Неверный номер телефона или пароль.')
        if not user.is_active:
            raise serializers.ValidationError('Аккаунт деактивирован.')
        attrs['user'] = user
        attrs['phone'] = phone
        return attrs


class SmsVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    sms_code = serializers.CharField(max_length=6)

    def validate(self, data):
        phone = data['phone'].strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not phone.startswith('+'):
            phone = '+' + phone.lstrip('8')
        data['phone'] = phone

        from apps.auth_app.sms_service import SMSService
        if not SMSService.verify_code(phone, data['sms_code']):
            raise serializers.ValidationError('Неверный или просроченный код подтверждения.')
        return data
