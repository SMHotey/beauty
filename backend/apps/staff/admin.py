from django.contrib import admin
from apps.staff.models import Master, MasterService


class MasterServiceInline(admin.TabularInline):
    model = MasterService
    extra = 1
    raw_id_fields = ('service',)
    fields = ('service', 'custom_price', 'custom_duration_minutes', 'is_enabled')


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username', 'phone')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
    list_display_links = ('get_full_name',)
    inlines = [MasterServiceInline]
    raw_id_fields = ('user',)

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Мастер'


@admin.register(MasterService)
class MasterServiceAdmin(admin.ModelAdmin):
    list_display = ('master', 'service', 'custom_price', 'custom_duration_minutes', 'is_enabled', 'created_at')
    search_fields = ('master__user__first_name', 'master__user__last_name', 'service__name')
    list_filter = ('is_enabled', 'service__category')
    list_editable = ('is_enabled',)
    list_display_links = ('master',)
    raw_id_fields = ('master', 'service')
