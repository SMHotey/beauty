from rest_framework import serializers
from apps.reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.phone', read_only=True)
    master_name = serializers.CharField(source='appointment.master.user.get_full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'client', 'client_name', 'appointment', 'master_name', 'rating', 'comment', 'photo', 'created_at']
        read_only_fields = ['id', 'client', 'client_name', 'master_name', 'created_at']
