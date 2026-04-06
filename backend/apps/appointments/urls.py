from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.appointments.views import (
    AppointmentViewSet,
    GuestAppointmentViewSet,
)

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'guest', GuestAppointmentViewSet, basename='appointment-guest')

urlpatterns = [
    path('', include(router.urls)),
]
