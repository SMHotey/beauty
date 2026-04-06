from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.auth_app.urls')),
    path('api/v1/services/', include('apps.services.urls')),
    path('api/v1/staff/', include('apps.staff.urls')),
    path('api/v1/staff/', include('apps.staff.master_urls')),
    path('api/v1/clients/', include('apps.clients.urls')),
    path('api/v1/appointments/', include('apps.appointments.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/promotions/', include('apps.promotions.urls')),
    path('api/v1/admin-panel/', include('apps.admin_panel.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/docs/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Beauty Salon Admin'
admin.site.site_title = 'Beauty Salon Admin Panel'
admin.site.index_title = 'Управление салоном красоты'
