from django.contrib import admin
from apps.reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'appointment', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['client__phone', 'comment', 'appointment__master__user__first_name', 'appointment__master__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
