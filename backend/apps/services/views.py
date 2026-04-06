from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.services.models import ServiceCategory, Service
from apps.services.serializers import ServiceCategorySerializer, ServiceSerializer


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    http_method_names = ['get', 'head', 'options']
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['order', 'name']
    ordering = ['order', 'name']


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.select_related('category').filter(is_active=True)
    serializer_class = ServiceSerializer
    http_method_names = ['get', 'head', 'options']
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'gender_target', 'is_active']
    search_fields = ['name']
    ordering_fields = ['base_price', 'base_duration_minutes', 'name']
    ordering = ['category__order', 'name']
