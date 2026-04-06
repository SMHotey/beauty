from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from apps.auth_app.serializers import (
    PhoneRegisterSerializer,
    PhoneLoginSerializer,
    SmsVerifySerializer,
)
from apps.auth_app.sms_service import SMSService


class PhoneRegisterView(generics.CreateAPIView):
    serializer_class = PhoneRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'phone': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class PhoneLoginView(generics.GenericAPIView):
    serializer_class = PhoneLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'phone': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


class SmsSendView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone')
        if not phone:
            return Response(
                {'detail': 'Поле phone обязательно.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        code = SMSService.send_code(phone)
        return Response({
            'detail': 'Код отправлен.',
            'phone': phone,
            'code': code,
        }, status=status.HTTP_200_OK)


class SmsVerifyView(generics.GenericAPIView):
    serializer_class = SmsVerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        user = User.objects.filter(username=phone).first()
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'verified': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'phone': user.username,
                },
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        return Response({
            'verified': True,
            'detail': 'Код подтверждён. Телефон готов к регистрации.',
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        client = getattr(user, 'client_profile', None)
        master = getattr(user, 'master_profile', None)

        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }

        if client:
            data['client'] = {
                'id': client.id,
                'phone': client.phone,
                'bonus_balance': client.bonus_balance,
                'referral_code': client.referral_code,
            }

        if master:
            data['master'] = {
                'id': master.id,
                'phone': master.phone,
                'photo': master.photo.url if master.photo else None,
                'bio': master.bio,
                'is_active': master.is_active,
            }

        return Response(data)
