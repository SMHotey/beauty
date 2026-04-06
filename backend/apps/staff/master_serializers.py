from rest_framework import serializers
from apps.staff.models import MasterSchedule


class MasterScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterSchedule
        fields = ['id', 'master', 'date', 'start_time', 'end_time', 'is_working', 'breaks']
        read_only_fields = ['id', 'master']


class MasterDashboardSerializer(serializers.Serializer):
    today_appointments = serializers.IntegerField()
    week_appointments = serializers.IntegerField()
    month_appointments = serializers.IntegerField()
    today_revenue = serializers.CharField()
    week_revenue = serializers.CharField()
    month_revenue = serializers.CharField()
    avg_rating = serializers.FloatField(allow_null=True)
    review_count = serializers.IntegerField()


class MasterAppointmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    client_name = serializers.CharField()
    client_phone = serializers.CharField(allow_null=True)
    datetime_start = serializers.DateTimeField()
    datetime_end = serializers.DateTimeField()
    status = serializers.CharField()
    payment_method = serializers.CharField()
    total_price = serializers.CharField()
    services = serializers.ListField(child=serializers.CharField())
    comment = serializers.CharField(allow_blank=True)


class MasterReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    client_name = serializers.CharField()
    rating = serializers.IntegerField()
    comment = serializers.CharField()
    created_at = serializers.DateTimeField()
    master_reply = serializers.CharField()
    service_name = serializers.CharField(allow_null=True)
