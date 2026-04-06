from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from datetime import datetime
from apps.staff.models import Master, MasterService
from apps.staff.serializers import MasterListSerializer, MasterSerializer, MasterServiceSerializer
from apps.appointments.utils import get_available_slots


class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.select_related('user').prefetch_related('master_services__service').filter(is_active=True)
    http_method_names = ['get', 'head', 'options']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'phone']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return MasterListSerializer
        return MasterSerializer

    def get_permissions(self):
        if self.action in ('slots', 'available_masters'):
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='available-masters')
    def available_masters(self, request):
        service_id = request.query_params.get('service_id')
        date_str = request.query_params.get('date')

        if not service_id or not date_str:
            raise ValidationError({'detail': 'Необходимы параметры: service_id, date'})

        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValidationError({'date': 'Неверный формат даты. Ожидается YYYY-MM-DD'})

        masters_qs = Master.objects.filter(
            is_active=True,
            master_services__service_id=service_id,
            master_services__is_enabled=True,
        ).select_related('user').distinct()

        results = []
        for master in masters_qs:
            slots = get_available_slots(master.id, date_str, [int(service_id)])
            results.append({
                'id': master.id,
                'full_name': master.user.get_full_name() or master.user.username,
                'bio': master.bio or '',
                'photo': master.photo.url if master.photo else None,
                'rating': master.rating,
                'review_count': master.review_count,
                'available_slots': slots,
            })

        return Response({'masters': results})

    @action(detail=True, methods=['get'], url_path='slots')
    def slots(self, request, pk=None):
        date = request.query_params.get('date')
        service_ids = request.query_params.get('service_ids', '')
        if not date:
            return Response({'error': 'Параметр date обязателен (YYYY-MM-DD)'}, status=400)
        ids = [int(x) for x in service_ids.split(',') if x.strip()]
        if not ids:
            return Response({'error': 'Параметр service_ids обязателен'}, status=400)
        slots = get_available_slots(pk, date, ids)
        return Response({'slots': slots})


class MasterServicesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = MasterServiceSerializer

    def get_queryset(self):
        return MasterService.objects.filter(
            master_id=self.kwargs['master_id'],
            is_enabled=True,
        ).select_related('service')
