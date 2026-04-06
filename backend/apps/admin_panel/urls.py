from django.urls import path
from apps.admin_panel.views import (
    DashboardStatsView,
    AdminMasterViewSet,
    AdminMasterServicesView,
    AdminCalendarView,
    AdminAppointmentViewSet,
    SalesReportView,
    SmsBroadcastView,
    AdminServiceViewSet,
    MasterStatsView,
    ClientStatsView,
    ServiceStatsView,
    MasterServiceStatsView,
    MasterPermissionsView,
    AdminStatsExportView,
)

admin_master = AdminMasterViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
admin_master_detail = AdminMasterViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

admin_appointment = AdminAppointmentViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
admin_appointment_detail = AdminAppointmentViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

admin_service = AdminServiceViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
admin_service_detail = AdminServiceViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='admin-dashboard-stats'),
    path('masters/', admin_master, name='admin-masters'),
    path('masters/<int:id>/', admin_master_detail, name='admin-master-detail'),
    path('masters/<int:master_id>/services/', AdminMasterServicesView.as_view(), name='admin-master-services'),
    path('calendar/', AdminCalendarView.as_view(), name='admin-calendar'),
    path('appointments/', admin_appointment, name='admin-appointments'),
    path('appointments/<int:id>/', admin_appointment_detail, name='admin-appointment-detail'),
    path('reports/sales/', SalesReportView.as_view(), name='admin-sales-report'),
    path('sms-broadcast/', SmsBroadcastView.as_view(), name='admin-sms-broadcast'),
    path('services/', admin_service, name='admin-services'),
    path('services/<int:id>/', admin_service_detail, name='admin-service-detail'),
    path('masters/<int:master_id>/stats/', MasterStatsView.as_view(), name='admin-master-stats'),
    path('clients/<int:client_id>/stats/', ClientStatsView.as_view(), name='admin-client-stats'),
    path('services/<int:service_id>/stats/', ServiceStatsView.as_view(), name='admin-service-stats'),
    path('masters/<int:master_id>/services/<int:service_id>/stats/', MasterServiceStatsView.as_view(), name='admin-master-service-stats'),
]
