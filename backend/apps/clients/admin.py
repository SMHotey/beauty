from django.contrib import admin
from apps.clients.models import Client, FavoriteMaster


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'bonus_balance', 'referral_code', 'referred_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['phone', 'referral_code']
    readonly_fields = ['referral_code', 'created_at', 'updated_at']


@admin.register(FavoriteMaster)
class FavoriteMasterAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'master', 'created_at']
    list_filter = ['created_at']
    search_fields = ['client__phone', 'master__user__first_name', 'master__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
