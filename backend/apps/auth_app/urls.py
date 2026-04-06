from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.auth_app.views import (
    PhoneRegisterView,
    PhoneLoginView,
    SmsSendView,
    SmsVerifyView,
    ProfileView,
)

urlpatterns = [
    path('register/', PhoneRegisterView.as_view(), name='auth-register'),
    path('login/', PhoneLoginView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('sms/send/', SmsSendView.as_view(), name='sms-send'),
    path('sms/verify/', SmsVerifyView.as_view(), name='sms-verify'),
    path('profile/', ProfileView.as_view(), name='auth-profile'),
]
