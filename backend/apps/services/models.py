from django.db import models
from apps.core.models import BaseModel


class ServiceCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Слаг')
    icon = models.CharField(max_length=50, verbose_name='Иконка')
    order = models.IntegerField(default=0, verbose_name='Порядок сортировки')

    class Meta:
        verbose_name = 'Категория услуг'
        verbose_name_plural = 'Категории услуг'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Service(BaseModel):
    GENDER_CHOICES = [
        ('female', 'Женская'),
        ('male', 'Мужская'),
        ('unisex', 'Унисекс'),
        ('children', 'Детская'),
    ]
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='Категория')
    name = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Слаг')
    description = models.TextField(default='', blank=True, verbose_name='Описание')
    base_duration_minutes = models.PositiveIntegerField(verbose_name='Длительность (мин)')
    base_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Базовая цена')
    gender_target = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex', verbose_name='Пол')
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['category__order', 'name']

    def __str__(self):
        return f"{self.category.name} — {self.name}"
