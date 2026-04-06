from rest_framework import serializers
from apps.staff.models import Master, MasterService


class MasterServiceSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    duration_minutes = serializers.IntegerField(read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_slug = serializers.SlugField(source='service.slug', read_only=True)

    class Meta:
        model = MasterService
        fields = (
            'id',
            'master',
            'service',
            'custom_price',
            'custom_duration_minutes',
            'is_enabled',
            'price',
            'duration_minutes',
            'service_name',
            'service_slug',
        )


class MasterListSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Master
        fields = (
            'id',
            'full_name',
            'phone',
            'photo',
            'bio',
            'is_active',
            'rating',
            'review_count',
        )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class MasterSerializer(serializers.ModelSerializer):
    rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    full_name = serializers.SerializerMethodField()
    services = MasterServiceSerializer(many=True, read_only=True, source='master_services')
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Master
        fields = (
            'id',
            'username',
            'email',
            'full_name',
            'phone',
            'photo',
            'bio',
            'is_active',
            'working_hours',
            'break_slots',
            'vacations',
            'rating',
            'review_count',
            'services',
        )

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
