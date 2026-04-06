import uuid
from django.db import models
from django.contrib.auth.models import User
from apps.core.models import BaseModel
from apps.staff.models import Master


class Client(BaseModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_profile', verbose_name='Пользователь')
    phone = models.CharField(max_length=20, unique=True, verbose_name='Телефон')
    bonus_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Бонусный баланс')
    referral_code = models.CharField(max_length=12, unique=True, verbose_name='Реферальный код')
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_clients', verbose_name='Пригласил')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.phone

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)


class FavoriteMaster(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='favorites', verbose_name='Клиент')
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='favorited_by', verbose_name='Мастер')

    class Meta:
        verbose_name = 'Избранный мастер'
        verbose_name_plural = 'Избранные мастера'
        unique_together = ['client', 'master']
        ordering = ['-created_at']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.client} — {self.master}"
