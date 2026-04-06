from django.urls import path
from apps.staff.master_views import (
    MasterDashboardView,
    MasterAppointmentsView,
    MasterReviewsView,
    MasterScheduleView,
    MasterProfileView,
)

urlpatterns = [
    path('master/dashboard/', MasterDashboardView.as_view(), name='master-dashboard'),
    path('master/profile/', MasterProfileView.as_view(), name='master-profile'),
    path('master/appointments/', MasterAppointmentsView.as_view(), name='master-appointments'),
    path('master/reviews/', MasterReviewsView.as_view(), name='master-reviews'),
    path('master/schedule/', MasterScheduleView.as_view(), name='master-schedule'),
]
