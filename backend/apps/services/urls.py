from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.services.views import ServiceCategoryViewSet, ServiceViewSet

router = DefaultRouter()
router.register('service-categories', ServiceCategoryViewSet, basename='servicecategory')
router.register('services', ServiceViewSet, basename='service')

urlpatterns = [
    path('', include(router.urls)),
]
