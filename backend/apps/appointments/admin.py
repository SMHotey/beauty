from django.contrib import admin
from apps.appointments.models import Appointment, AppointmentService


class AppointmentServiceInline(admin.TabularInline):
    model = AppointmentService
    extra = 1
    fields = ['service', 'price_at_booking', 'duration_at_booking']
    readonly_fields = ['price_at_booking', 'duration_at_booking']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'master', 'datetime_start', 'datetime_end', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['client__phone', 'master__user__first_name', 'master__user__last_name']
    readonly_fields = ['total_price', 'created_at', 'updated_at']
    inlines = [AppointmentServiceInline]
    date_hierarchy = 'datetime_start'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('client', 'master__user')


@admin.register(AppointmentService)
class AppointmentServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'service', 'price_at_booking', 'duration_at_booking']
    list_filter = ['created_at']
    search_fields = ['appointment__client__phone', 'service__name']
    readonly_fields = ['created_at', 'updated_at']
