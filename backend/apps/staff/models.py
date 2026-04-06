from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from apps.services.models import Service


class Master(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='master_profile', verbose_name='Пользователь')
    phone = models.CharField(max_length=20, unique=True, verbose_name='Телефон')
    photo = models.ImageField(upload_to='masters/', blank=True, null=True, verbose_name='Фото')
    bio = models.TextField(blank=True, verbose_name='О себе')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    working_hours = models.JSONField(default=dict, verbose_name='Рабочие часы (по дням недели)')
    break_slots = models.JSONField(default=list, verbose_name='Перерывы')
    vacations = models.JSONField(default=list, verbose_name='Отпуска')
    _cached_rating = models.FloatField(null=True, blank=True, verbose_name='Кэшированный рейтинг')

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['user__first_name', 'user__last_name']
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    @property
    def rating(self):
        if self._cached_rating is not None:
            return round(self._cached_rating, 1)
        from apps.reviews.models import Review
        result = Review.objects.filter(appointment__master=self).aggregate(models.Avg('rating'))
        avg = result['rating__avg']
        if avg is not None:
            self._cached_rating = avg
            self.save(update_fields=['_cached_rating'])
            return round(avg, 1)
        return None

    @property
    def rating(self):
        if self._cached_rating is not None:
            return round(self._cached_rating, 1)
        from apps.reviews.models import Review
        result = Review.objects.filter(appointment__master=self).aggregate(models.Avg('rating'))
        avg = result['rating__avg']
        if avg is not None:
            self._cached_rating = avg
            self.save(update_fields=['_cached_rating'])
            return round(avg, 1)
        return None

    @property
    def review_count(self):
        from django.db.models import Count
        from apps.reviews.models import Review
        return Review.objects.filter(appointment__master=self).count()


class MasterPermission(BaseModel):
    master = models.OneToOneField(Master, on_delete=models.CASCADE, related_name='permissions', verbose_name='Мастер')
    can_edit_schedule = models.BooleanField(default=False, verbose_name='Может редактировать график')
    can_reply_reviews = models.BooleanField(default=False, verbose_name='Может отвечать на отзывы')

    class Meta:
        verbose_name = 'Разрешения мастера'
        verbose_name_plural = 'Разрешения мастеров'

    def __str__(self):
        return f"Разрешения: {self.master}"


class MasterSchedule(BaseModel):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='schedules', verbose_name='Мастер')
    date = models.DateField(verbose_name='Дата')
    start_time = models.CharField(max_length=5, verbose_name='Начало')
    end_time = models.CharField(max_length=5, verbose_name='Конец')
    is_working = models.BooleanField(default=True, verbose_name='Рабочий день')
    breaks = models.JSONField(default=list, blank=True, verbose_name='Перерывы')

    class Meta:
        verbose_name = 'Расписание мастера'
        verbose_name_plural = 'Расписания мастеров'
        unique_together = ['master', 'date']
        ordering = ['date']

    def __str__(self):
        status = 'рабочий' if self.is_working else 'выходной'
        return f"{self.master} — {self.date} ({status})"


class MasterService(BaseModel):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='master_services', verbose_name='Мастер')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='master_services', verbose_name='Услуга')
    custom_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name='Кастомная цена')
    custom_duration_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name='Кастомная длительность')
    is_enabled = models.BooleanField(default=True, verbose_name='Включена')

    class Meta:
        verbose_name = 'Услуга мастера'
        verbose_name_plural = 'Услуги мастеров'
        unique_together = ['master', 'service']

    def __str__(self):
        return f"{self.master} — {self.service}"

    @property
    def price(self):
        return self.custom_price if self.custom_price is not None else self.service.base_price

    @property
    def duration_minutes(self):
        return self.custom_duration_minutes if self.custom_duration_minutes is not None else self.service.base_duration_minutes
