from django.contrib import admin
from apps.promotions.models import Promotion, GiftCertificate, BlacklistedClient, Setting


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'discount_percent', 'start_date', 'end_date', 'promo_code']
    list_filter = ['start_date', 'end_date']
    search_fields = ['name', 'description', 'promo_code']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    filter_horizontal = ['applicable_services']


@admin.register(GiftCertificate)
class GiftCertificateAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'nominal', 'buyer_name', 'recipient_email', 'is_used', 'used_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['code', 'buyer_name', 'recipient_email']
    readonly_fields = ['code', 'created_at', 'updated_at']


@admin.register(BlacklistedClient)
class BlacklistedClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'reason', 'created_at']
    search_fields = ['client__phone', 'reason']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ['id', 'key', 'value']
    search_fields = ['key', 'value']
    readonly_fields = ['created_at', 'updated_at']
