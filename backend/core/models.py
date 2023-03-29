from django.db import models
from django.core.validators import RegexValidator
from colorfield.fields import ColorField


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(max_length=200, verbose_name='название')
    color = ColorField(
        default='#FFFFFF',
        null=True,
        max_length=7,
        verbose_name='цвет'
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
        null=True,
        validators=[RegexValidator(regex='^[-а-я-a-zA-Z0-9_]+$')],
        verbose_name='слаг'
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=200, verbose_name='название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name
