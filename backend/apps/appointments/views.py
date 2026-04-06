from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from rest_framework import viewsets, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.throttling import AnonRateThrottle
from django.conf import settings
from apps.appointments.models import Appointment, AppointmentService
from apps.appointments.serializers import (
    AppointmentSerializer,
    GuestAppointmentSerializer,
    AppointmentCreateSerializer,
)
from apps.appointments.utils import get_available_slots
from apps.clients.models import Client
from apps.services.models import Service


class GuestAppointmentThrottle(AnonRateThrottle):
    rate = '10/hour'


class AppointmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        client = Client.objects.filter(user=self.request.user).first()
        if not client:
            return Appointment.objects.none()
        return Appointment.objects.filter(client=client).prefetch_related('services__service').select_related('master__user')

    def get_object(self):
        """Override to return 403 instead of 404 for permission denied."""
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        filter_kwargs = {self.lookup_field: lookup_value}
        obj = queryset.filter(**filter_kwargs).first()
        if obj is None:
            # If the object exists but doesn't belong to this user, return 403
            from apps.appointments.models import Appointment
            if Appointment.objects.filter(**filter_kwargs).exists():
                raise PermissionDenied('Доступ запрещён.')
            from rest_framework.exceptions import NotFound
            raise NotFound()
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        client = Client.objects.filter(user=self.request.user).first()
        if not client:
            raise ValidationError({'detail': 'Профиль клиента не найден.'})

        validated = serializer.validated_data
        master = validated['master']
        service_ids = validated['service_ids']
        datetime_start = validated['datetime_start']
        datetime_end = validated['datetime_end']
        comment = validated.get('comment', '')
        use_bonuses = validated.get('use_bonuses', False)

        with transaction.atomic():
            appointment = Appointment.objects.create(
                client=client,
                master=master,
                datetime_start=datetime_start,
                datetime_end=datetime_end,
                comment=comment,
            )

            from apps.staff.models import MasterService
            for sid in service_ids:
                ms = MasterService.objects.filter(master=master, service_id=sid, is_enabled=True).first()
                if ms:
                    price = ms.price
                    duration = ms.duration_minutes
                else:
                    svc = Service.objects.get(id=sid)
                    price = svc.base_price
                    duration = svc.base_duration_minutes

                AppointmentService.objects.create(
                    appointment=appointment,
                    service_id=sid,
                    price_at_booking=price,
                    duration_at_booking=duration,
                )

            total = appointment.services.aggregate(total=Sum('price_at_booking'))['total'] or 0

            if use_bonuses and client.bonus_balance > 0:
                max_bonus = int(total * 0.3)
                bonus_to_use = min(int(client.bonus_balance), max_bonus)
                total -= bonus_to_use
                client.bonus_balance -= bonus_to_use
                client.save(update_fields=['bonus_balance'])

            appointment.total_price = total
            appointment.save()

    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        master_id = request.query_params.get('master_id')
        date_str = request.query_params.get('date')
        service_ids_param = request.query_params.get('service_ids')

        if not master_id or not date_str or not service_ids_param:
            raise ValidationError({
                'detail': 'Необходимы параметры: master_id, date, service_ids'
            })

        try:
            service_ids = [int(x) for x in service_ids_param.split(',')]
        except (ValueError, TypeError):
            raise ValidationError({'service_ids': 'Неверный формат service_ids.'})

        slots = get_available_slots(master_id, date_str, service_ids)
        return Response({'slots': slots})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status not in ('pending', 'confirmed'):
            raise ValidationError({'detail': 'Невозможно отменить запись в текущем статусе.'})

        cancellation_hours = getattr(settings, 'CANCELLATION_HOURS', 2)
        now = timezone.now()
        if appointment.datetime_start <= now + timedelta(hours=cancellation_hours):
            raise ValidationError({
                'detail': f'Отмена возможна не позднее чем за {cancellation_hours} часа до записи.'
            })

        appointment.status = 'cancelled_by_client'
        appointment.save()

        serializer = self.get_serializer(appointment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def repeat(self, request, pk=None):
        original = self.get_object()

        services = original.services.all()
        if not services.exists():
            raise ValidationError({'detail': 'У исходной записи нет услуг.'})

        service_ids = list(services.values_list('service_id', flat=True))

        with transaction.atomic():
            appointment = Appointment.objects.create(
                client=original.client,
                master=original.master,
                datetime_start=original.datetime_start,
                datetime_end=original.datetime_end,
                comment=original.comment,
            )

            for appt_service in services:
                AppointmentService.objects.create(
                    appointment=appointment,
                    service=appt_service.service,
                    price_at_booking=appt_service.price_at_booking,
                    duration_at_booking=appt_service.duration_at_booking,
                )

            appointment.total_price = appointment.services.aggregate(total=Sum('price_at_booking'))['total'] or 0
            appointment.save()

        serializer = self.get_serializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GuestAppointmentViewSet(viewsets.GenericViewSet):
    serializer_class = GuestAppointmentSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [GuestAppointmentThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        phone = validated.get('phone', '')

        if phone:
            client, _ = Client.objects.get_or_create(
                phone=phone,
                defaults={'user': None}
            )
        else:
            client = None

        master = validated['master']
        service_ids = validated['service_ids']
        datetime_start = validated['datetime_start']
        datetime_end = validated['datetime_end']
        comment = validated.get('comment', '')

        with transaction.atomic():
            appointment = Appointment.objects.create(
                client=client,
                master=master,
                datetime_start=datetime_start,
                datetime_end=datetime_end,
                comment=comment,
            )

            from apps.staff.models import MasterService
            for sid in service_ids:
                ms = MasterService.objects.filter(master=master, service_id=sid, is_enabled=True).first()
                if ms:
                    price = ms.price
                    duration = ms.duration_minutes
                else:
                    svc = Service.objects.get(id=sid)
                    price = svc.base_price
                    duration = svc.base_duration_minutes

                AppointmentService.objects.create(
                    appointment=appointment,
                    service_id=sid,
                    price_at_booking=price,
                    duration_at_booking=duration,
                )

            appointment.total_price = appointment.services.aggregate(total=Sum('price_at_booking'))['total'] or 0
            appointment.save()

        output_serializer = AppointmentSerializer(appointment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
