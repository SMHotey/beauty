from django.db import models


class BaseModel(models.Model):
    """
    Базовая абстрактная модель для всех моделей проекта.
    Предоставляет поля для отслеживания времени создания и обновления записей.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True
        verbose_name = "Базовая модель"
        verbose_name_plural = "Базовые модели"
