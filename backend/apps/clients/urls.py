from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.clients.views import ClientProfileViewSet, FavoriteMasterViewSet

router = DefaultRouter()
router.register(r'profile', ClientProfileViewSet, basename='client-profile')
router.register(r'favorites', FavoriteMasterViewSet, basename='favorite-masters')

urlpatterns = [
    path('', include(router.urls)),
]
