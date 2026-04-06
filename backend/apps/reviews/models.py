from django.db import models
from apps.core.models import BaseModel
from apps.clients.models import Client
from apps.appointments.models import Appointment


class Review(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='reviews', verbose_name='Клиент')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='review', verbose_name='Запись')
    rating = models.PositiveSmallIntegerField(verbose_name='Оценка', choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(verbose_name='Комментарий')
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True, verbose_name='Фото')
    master_reply = models.TextField(blank=True, default='', verbose_name='Ответ мастера')
    is_deleted = models.BooleanField(default=False, verbose_name='Удалён')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client} — {self.rating}★ — {self.appointment.master}"
