from datetime import datetime, timedelta, date
from decimal import Decimal

from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from apps.staff.models import Master, MasterSchedule, MasterPermission
from apps.appointments.models import Appointment
from apps.reviews.models import Review
from apps.staff.master_serializers import (
    MasterDashboardSerializer,
    MasterAppointmentSerializer,
    MasterScheduleSerializer,
    MasterReviewSerializer,
)


class IsMasterUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, 'master_profile')


class MasterDashboardView(generics.GenericAPIView):
    permission_classes = [IsMasterUser]

    def get(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        today_apts = Appointment.objects.filter(master=master, datetime_start__gte=today_start, datetime_start__lt=today_start + timedelta(days=1))
        week_apts = Appointment.objects.filter(master=master, datetime_start__gte=week_start)
        month_apts = Appointment.objects.filter(master=master, datetime_start__gte=month_start)

        today_revenue = today_apts.filter(status='completed').aggregate(total=Sum('total_price'))['total'] or Decimal('0')
        week_revenue = week_apts.filter(status='completed').aggregate(total=Sum('total_price'))['total'] or Decimal('0')
        month_revenue = month_apts.filter(status='completed').aggregate(total=Sum('total_price'))['total'] or Decimal('0')

        avg_rating = Review.objects.filter(appointment__master=master, is_deleted=False).aggregate(avg=Avg('rating'))['avg']
        review_count = Review.objects.filter(appointment__master=master, is_deleted=False).count()

        data = {
            'today_appointments': today_apts.count(),
            'week_appointments': week_apts.count(),
            'month_appointments': month_apts.count(),
            'today_revenue': str(today_revenue),
            'week_revenue': str(week_revenue),
            'month_revenue': str(month_revenue),
            'avg_rating': round(avg_rating, 1) if avg_rating else None,
            'review_count': review_count,
        }
        return Response(data)


class MasterAppointmentsView(generics.GenericAPIView):
    permission_classes = [IsMasterUser]

    def get(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        status_filter = request.query_params.get('status')

        qs = Appointment.objects.filter(master=master).order_by('-datetime_start')

        if date_from:
            qs = qs.filter(datetime_start__gte=datetime.fromisoformat(date_from).replace(tzinfo=timezone.get_current_timezone()))
        if date_to:
            qs = qs.filter(datetime_start__lte=datetime.fromisoformat(date_to).replace(tzinfo=timezone.get_current_timezone(), hour=23, minute=59, second=59))
        if status_filter:
            qs = qs.filter(status=status_filter)

        appointments = []
        for apt in qs[:50]:
            client_name = 'Гость'
            client_phone = None
            if apt.client:
                client_name = f"{apt.client.user.first_name} {apt.client.user.last_name}".strip() or apt.client.user.username
                client_phone = apt.client.phone

            appointments.append({
                'id': apt.id,
                'client_name': client_name,
                'client_phone': client_phone,
                'datetime_start': apt.datetime_start.isoformat(),
                'datetime_end': apt.datetime_end.isoformat() if apt.datetime_end else '',
                'status': apt.status,
                'payment_method': apt.payment_method,
                'total_price': str(apt.total_price or 0),
                'services': [s.service.name for s in apt.services.all()],
                'comment': apt.comment or '',
            })

        return Response(appointments)

    def patch(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})

        apt_id = request.data.get('appointment_id')
        new_status = request.data.get('status')

        if not apt_id or not new_status:
            raise ValidationError({'detail': 'appointment_id и status обязательны.'})

        try:
            apt = Appointment.objects.get(id=apt_id, master=master)
        except Appointment.DoesNotExist:
            raise ValidationError({'detail': 'Запись не найдена.'})

        apt.status = new_status
        apt.save()
        return Response({'status': apt.status})


class MasterReviewsView(generics.GenericAPIView):
    permission_classes = [IsMasterUser]

    def get(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})

        reviews_qs = Review.objects.filter(
            appointment__master=master,
            is_deleted=False,
        ).select_related('client__user', 'appointment').order_by('-created_at')

        reviews = []
        for r in reviews_qs:
            client_name = f"{r.client.user.first_name} {r.client.user.last_name}".strip() if r.client and r.client.user else 'Гость'
            service_name = None
            if r.appointment:
                first_svc = r.appointment.services.first()
                if first_svc:
                    service_name = first_svc.service.name

            reviews.append({
                'id': r.id,
                'client_name': client_name,
                'rating': r.rating,
                'comment': r.comment,
                'created_at': r.created_at.isoformat(),
                'master_reply': r.master_reply or '',
                'service_name': service_name,
            })

        return Response(reviews)

    def patch(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
            perms = master.permissions
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})
        except MasterPermission.DoesNotExist:
            raise ValidationError({'detail': 'У вас нет разрешения отвечать на отзывы.'})

        if not perms.can_reply_reviews:
            raise ValidationError({'detail': 'У вас нет разрешения отвечать на отзывы.'})

        review_id = request.data.get('review_id')
        reply = request.data.get('reply', '')

        if not review_id:
            raise ValidationError({'detail': 'review_id обязателен.'})

        try:
            review = Review.objects.get(id=review_id, appointment__master=master)
        except Review.DoesNotExist:
            raise ValidationError({'detail': 'Отзыв не найден.'})

        review.master_reply = reply
        review.save()
        return Response({'master_reply': reply})


class MasterScheduleView(generics.GenericAPIView):
    permission_classes = [IsMasterUser]

    def get(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        qs = MasterSchedule.objects.filter(master=master).order_by('date')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        serializer = MasterScheduleSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
            perms = master.permissions
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})
        except MasterPermission.DoesNotExist:
            raise ValidationError({'detail': 'У вас нет разрешения редактировать график.'})

        if not perms.can_edit_schedule:
            raise ValidationError({'detail': 'У вас нет разрешения редактировать график.'})

        date_str = request.data.get('date')
        if not date_str:
            raise ValidationError({'detail': 'Дата обязательна.'})

        schedule, created = MasterSchedule.objects.update_or_create(
            master=master,
            date=date_str,
            defaults={
                'start_time': request.data.get('start_time', '10:00'),
                'end_time': request.data.get('end_time', '19:00'),
                'is_working': request.data.get('is_working', True),
                'breaks': request.data.get('breaks', []),
            }
        )
        serializer = MasterScheduleSerializer(schedule)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def delete(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
            perms = master.permissions
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})
        except MasterPermission.DoesNotExist:
            raise ValidationError({'detail': 'У вас нет разрешения редактировать график.'})

        if not perms.can_edit_schedule:
            raise ValidationError({'detail': 'У вас нет разрешения редактировать график.'})

        schedule_id = request.data.get('schedule_id')
        if not schedule_id:
            raise ValidationError({'detail': 'schedule_id обязателен.'})

        try:
            schedule = MasterSchedule.objects.get(id=schedule_id, master=master)
            schedule.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MasterSchedule.DoesNotExist:
            raise ValidationError({'detail': 'Расписание не найдено.'})


class MasterProfileView(generics.GenericAPIView):
    permission_classes = [IsMasterUser]

    def get(self, request, *args, **kwargs):
        try:
            master = request.user.master_profile
            perms = master.permissions
        except Master.DoesNotExist:
            raise ValidationError({'detail': 'Профиль мастера не найден.'})
        except MasterPermission.DoesNotExist:
            perms = None

        return Response({
            'id': master.id,
            'full_name': f"{master.user.first_name} {master.user.last_name}".strip() or master.user.username,
            'phone': master.phone,
            'bio': master.bio,
            'photo': master.photo.url if master.photo else None,
            'is_active': master.is_active,
            'rating': master.rating,
            'review_count': master.review_count,
            'permissions': {
                'can_edit_schedule': perms.can_edit_schedule if perms else False,
                'can_reply_reviews': perms.can_reply_reviews if perms else False,
            } if perms else {'can_edit_schedule': False, 'can_reply_reviews': False},
        })
