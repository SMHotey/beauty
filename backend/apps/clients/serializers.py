from rest_framework import serializers
from apps.clients.models import Client, FavoriteMaster


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'user', 'phone', 'bonus_balance', 'referral_code', 'referred_by']
        read_only_fields = ['id', 'bonus_balance', 'referral_code']


class FavoriteMasterSerializer(serializers.ModelSerializer):
    master_name = serializers.CharField(source='master.user.get_full_name', read_only=True)
    master_photo = serializers.CharField(source='master.photo', read_only=True)
    master_bio = serializers.CharField(source='master.bio', read_only=True)
    master_rating = serializers.DecimalField(max_digits=3, decimal_places=1, source='master.rating', read_only=True)
    master_id = serializers.IntegerField(source='master.id', read_only=True)

    class Meta:
        model = FavoriteMaster
        fields = ['id', 'client', 'master', 'master_id', 'master_name', 'master_photo', 'master_bio', 'master_rating']
        read_only_fields = ['id', 'client', 'master_name', 'master_photo', 'master_bio', 'master_rating', 'master_id']
