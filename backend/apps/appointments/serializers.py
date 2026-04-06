from datetime import timedelta
from rest_framework import serializers
from apps.appointments.models import Appointment, AppointmentService
from django.utils import timezone


class AppointmentServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = AppointmentService
        fields = ['id', 'service', 'service_name', 'price_at_booking', 'duration_at_booking']
        read_only_fields = ['id', 'service_name']


class AppointmentSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.user.get_full_name', read_only=True)
    services = AppointmentServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'client', 'master', 'master_name', 'services', 'datetime_start', 'datetime_end', 'status', 'total_price', 'comment', 'created_at']
        read_only_fields = ['id', 'client', 'status', 'total_price', 'created_at', 'master_name']


def get_master_queryset():
    from apps.staff.models import Master
    return Master.objects.filter(is_active=True)


class _AppointmentValidationMixin:
    """Shared validation logic for appointment booking serializers."""

    def validate_master_id(self, value):
        from apps.staff.models import Master
        try:
            return Master.objects.get(pk=value, is_active=True)
        except Master.DoesNotExist:
            raise serializers.ValidationError('Мастер не найден или не активен.')

    def validate_datetime_start(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError('Время записи должно быть в будущем.')
        return value

    def _calculate_duration_and_end(self, master, service_ids, datetime_start):
        total_duration = 0
        from apps.staff.models import MasterService
        from apps.services.models import Service
        for sid in service_ids:
            ms = MasterService.objects.filter(master=master, service_id=sid, is_enabled=True).first()
            if ms:
                total_duration += ms.duration_minutes
            else:
                s = Service.objects.get(id=sid)
                total_duration += s.base_duration_minutes

        datetime_end = datetime_start + timedelta(minutes=total_duration)

        existing = master.appointments.filter(
            datetime_start__lt=datetime_end,
            datetime_end__gt=datetime_start,
            status__in=['pending', 'confirmed']
        ).exists()

        if existing:
            raise serializers.ValidationError({
                'datetime_start': 'Выбранное время уже занято.'
            })

        return datetime_end


class GuestAppointmentSerializer(_AppointmentValidationMixin, serializers.Serializer):
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    master_id = serializers.IntegerField(help_text='ID мастера')
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='Список ID услуг'
    )
    datetime_start = serializers.DateTimeField(help_text='Дата и время начала записи')
    comment = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, data):
        master = data['master_id']
        service_ids = data['service_ids']
        datetime_start = data['datetime_start']

        datetime_end = self._calculate_duration_and_end(master, service_ids, datetime_start)

        data['datetime_end'] = datetime_end
        data['master'] = master
        data.pop('master_id')
        return data


class AppointmentCreateSerializer(_AppointmentValidationMixin, serializers.Serializer):
    master_id = serializers.IntegerField(help_text='ID мастера')
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='Список ID услуг'
    )
    datetime_start = serializers.DateTimeField(help_text='Дата и время начала записи')
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    use_bonuses = serializers.BooleanField(default=False, required=False)

    def validate(self, data):
        master = data['master_id']
        service_ids = data['service_ids']
        datetime_start = data['datetime_start']

        datetime_end = self._calculate_duration_and_end(master, service_ids, datetime_start)

        data['datetime_end'] = datetime_end
        data['master'] = master
        data.pop('master_id')
        return data


class AppointmentCreateSerializer(_AppointmentValidationMixin, serializers.Serializer):
    master_id = serializers.IntegerField(help_text='ID мастера')
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='Список ID услуг'
    )
    datetime_start = serializers.DateTimeField(help_text='Дата и время начала записи')
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    use_bonuses = serializers.BooleanField(default=False, required=False)

    def validate(self, data):
        master = data['master_id']
        service_ids = data['service_ids']
        datetime_start = data['datetime_start']

        datetime_end = self._calculate_duration_and_end(master, service_ids, datetime_start)

        data['datetime_end'] = datetime_end
        data['master'] = master
        data.pop('master_id')
        return data
