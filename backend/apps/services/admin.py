from django.contrib import admin
from apps.services.models import ServiceCategory, Service


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    list_display_links = ('name',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'base_price', 'base_duration_minutes', 'gender_target', 'is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'gender_target', 'is_active')
    list_editable = ('is_active',)
    list_display_links = ('name',)
