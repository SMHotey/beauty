from django.db import models
from apps.core.models import BaseModel
from apps.clients.models import Client
from apps.staff.models import Master
from apps.services.models import Service


class Appointment(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('completed', 'Завершена'),
        ('cancelled_by_client', 'Отменена клиентом'),
        ('cancelled_by_admin', 'Отменена администратором'),
        ('no_show', 'Не явился'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
        ('promo', 'Акция'),
        ('certificate', 'Сертификат'),
    ]
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments', verbose_name='Клиент')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='appointments', verbose_name='Мастер')
    datetime_start = models.DateTimeField(verbose_name='Начало')
    datetime_end = models.DateTimeField(verbose_name='Конец')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash', verbose_name='Способ оплаты')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Итоговая цена')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    reminder_sent = models.BooleanField(default=False, verbose_name='Напоминание отправлено')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-datetime_start']

    def __str__(self):
        client_str = self.client.phone if self.client else 'Гость'
        return f"{client_str} — {self.master} — {self.datetime_start}"

    def save(self, *args, **kwargs):
        if self.pk:
            total = self.services.aggregate(
                total=models.Sum(models.F('price_at_booking'))
            )['total']
            if total is not None:
                self.total_price = total
        super().save(*args, **kwargs)


class AppointmentService(BaseModel):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='services', verbose_name='Запись')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    price_at_booking = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Цена на момент записи')
    duration_at_booking = models.PositiveIntegerField(verbose_name='Длительность на момент записи')

    class Meta:
        verbose_name = 'Услуга в записи'
        verbose_name_plural = 'Услуги в записях'

    def __str__(self):
        return f"{self.appointment} — {self.service} ({self.price_at_booking})"
