from rest_framework import serializers
from apps.services.models import ServiceCategory, Service


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'slug', 'icon', 'order')


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    masters = serializers.SerializerMethodField()

    class Meta:
        model = Service
        fields = (
            'id',
            'category',
            'name',
            'slug',
            'description',
            'base_duration_minutes',
            'base_price',
            'gender_target',
            'is_active',
            'category_name',
            'masters',
        )
        extra_kwargs = {
            'slug': {'required': False},
        }

    def get_masters(self, obj):
        from apps.staff.models import MasterService
        return [
            {
                'id': ms.master.id,
                'full_name': f"{ms.master.user.first_name} {ms.master.user.last_name}".strip() or ms.master.user.username,
                'is_active': ms.master.is_active,
            }
            for ms in MasterService.objects.filter(service=obj, is_enabled=True).select_related('master__user')
        ]

    def create(self, validated_data):
        if not validated_data.get('slug'):
            from django.utils.text import slugify
            base_slug = slugify(validated_data['name'], allow_unicode=True)
            slug = base_slug
            counter = 1
            while Service.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            validated_data['slug'] = slug
        return super().create(validated_data)
