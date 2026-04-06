from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.staff.views import MasterViewSet, MasterServicesView

router = DefaultRouter()
router.register('masters', MasterViewSet, basename='master')

urlpatterns = [
    path('', include(router.urls)),
    path('masters/<int:master_id>/services/', MasterServicesView.as_view(), name='master-services'),
]
