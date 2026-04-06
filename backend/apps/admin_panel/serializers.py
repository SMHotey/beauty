from rest_framework import serializers
from apps.staff.models import Master, MasterService
from apps.appointments.models import Appointment
from django.db.models import Sum, Count, Avg


class DashboardStatsSerializer(serializers.Serializer):
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    appointments_count = serializers.IntegerField()
    masters_count = serializers.IntegerField()
    clients_count = serializers.IntegerField()
    avg_check = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    top_services = serializers.ListField(child=serializers.DictField())
    master_load = serializers.ListField(child=serializers.DictField())

    def to_representation(self, instance):
        return instance


class MasterCalendarSerializer(serializers.Serializer):
    master_id = serializers.IntegerField()
    master_name = serializers.CharField()
    date = serializers.DateField()
    appointments = serializers.ListField(child=serializers.DictField())

    def to_representation(self, instance):
        return instance


class AdminAppointmentSerializer(serializers.ModelSerializer):
    client_name = serializers.SerializerMethodField()
    client_phone = serializers.SerializerMethodField()
    client_id = serializers.IntegerField(source='client.id', read_only=True, allow_null=True)
    master_id = serializers.IntegerField(source='master.id', read_only=True)
    master_name = serializers.CharField(source='master.user.get_full_name', read_only=True)
    service_names = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id', 'client_id', 'client_name', 'client_phone', 'master_id', 'master_name',
            'datetime_start', 'datetime_end', 'status', 'total_price',
            'comment', 'service_names', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price']

    def get_client_name(self, obj):
        if obj.client and obj.client.user:
            full = f"{obj.client.user.first_name} {obj.client.user.last_name}".strip()
            return full or obj.client.phone
        return 'Гость'

    def get_client_phone(self, obj):
        return obj.client.phone if obj.client else None

    def get_service_names(self, obj):
        return [s.service.name for s in obj.services.all()]


class SalesReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    appointments_count = serializers.IntegerField()
    avg_check = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)

    def to_representation(self, instance):
        return instance
