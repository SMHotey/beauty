import uuid
from django.db import models
from apps.core.models import BaseModel
from apps.services.models import Service


class Promotion(BaseModel):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Скидка (%)')
    applicable_services = models.ManyToManyField(Service, blank=True, verbose_name='Применимые услуги')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    promo_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='Промокод')

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class GiftCertificate(BaseModel):
    code = models.CharField(max_length=12, unique=True, verbose_name='Код')
    nominal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Номинал')
    buyer_name = models.CharField(max_length=200, verbose_name='Имя покупателя')
    recipient_email = models.EmailField(verbose_name='Email получателя')
    is_used = models.BooleanField(default=False, verbose_name='Использован')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата использования')

    class Meta:
        verbose_name = 'Подарочный сертификат'
        verbose_name_plural = 'Подарочные сертификаты'

    def __str__(self):
        return f"{self.code} — {self.nominal}₽"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)


class BlacklistedClient(BaseModel):
    client = models.OneToOneField('clients.Client', on_delete=models.CASCADE, related_name='blacklist_entry', verbose_name='Клиент')
    reason = models.TextField(verbose_name='Причина')

    class Meta:
        verbose_name = 'Чёрный список'
        verbose_name_plural = 'Чёрный список'

    def __str__(self):
        return f"{self.client} — {self.reason[:50]}"


class Setting(BaseModel):
    key = models.CharField(max_length=100, unique=True, verbose_name='Ключ')
    value = models.TextField(verbose_name='Значение')

    class Meta:
        verbose_name = 'Настройка'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return f"{self.key} = {self.value}"
