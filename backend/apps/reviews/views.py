from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from apps.reviews.models import Review
from apps.reviews.serializers import ReviewSerializer
from apps.clients.models import Client
from apps.appointments.models import Appointment


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Review.objects.select_related('client', 'appointment__master__user')
        master_id = self.request.query_params.get('master_id')
        if master_id:
            qs = qs.filter(appointment__master_id=master_id)
        return qs

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        client = Client.objects.filter(user=self.request.user).first()
        if not client:
            raise ValidationError({'detail': 'Профиль клиента не найден.'})

        appointment_id = self.request.data.get('appointment')
        if not appointment_id:
            raise ValidationError({'appointment': 'Это поле обязательно.'})

        try:
            appointment = Appointment.objects.get(id=appointment_id, client=client)
        except Appointment.DoesNotExist:
            raise ValidationError({'appointment': 'Запись не найдена или не принадлежит вам.'})

        if appointment.status != 'completed':
            raise ValidationError({'appointment': 'Отзыв можно оставить только для завершённой записи.'})

        if Review.objects.filter(appointment=appointment).exists():
            raise ValidationError({'appointment': 'Отзыв для этой записи уже существует.'})

        serializer.save(client=client, appointment=appointment)
