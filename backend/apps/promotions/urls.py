from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.promotions.views import PromotionViewSet, GiftCertificateViewSet, BlacklistedClientViewSet

router = DefaultRouter()
router.register(r'promotions', PromotionViewSet, basename='promotions')
router.register(r'gift-certificates', GiftCertificateViewSet, basename='gift-certificates')
router.register(r'blacklist', BlacklistedClientViewSet, basename='blacklist')

urlpatterns = [
    path('', include(router.urls)),
]
