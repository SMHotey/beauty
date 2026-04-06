from rest_framework import serializers
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient
from apps.services.models import Service


class PromotionSerializer(serializers.ModelSerializer):
    applicable_service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    applicable_services = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Promotion
        fields = ['id', 'name', 'description', 'discount_percent', 'applicable_services', 'applicable_service_ids', 'start_date', 'end_date', 'promo_code', 'is_active']
        read_only_fields = ['id', 'applicable_services']

    def update(self, instance, validated_data):
        service_ids = validated_data.pop('applicable_service_ids', None)
        instance = super().update(instance, validated_data)
        if service_ids is not None:
            instance.applicable_services.set(service_ids)
        return instance


class GiftCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCertificate
        fields = ['id', 'code', 'nominal', 'buyer_name', 'recipient_email', 'is_used']
        read_only_fields = ['id', 'code', 'is_used']


class GiftCertificateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiftCertificate
        fields = ['nominal', 'buyer_name', 'recipient_email']


class BlacklistedClientSerializer(serializers.ModelSerializer):
    client_phone = serializers.CharField(source='client.phone', read_only=True)

    class Meta:
        model = BlacklistedClient
        fields = ['id', 'client', 'client_phone', 'reason', 'created_at']
        read_only_fields = ['id', 'client_phone', 'created_at']
