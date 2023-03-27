from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Модель пользователей"""
    email = models.EmailField(unique=True, max_length=254)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(regex='^[\w.@+-]+$')]
    )
    password = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписок"""
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authors')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(fields=['subscriber', 'author'],
                                    name='unique_subscribe')
        ]

    def __str__(self):
        return f'{self.subscriber} - {self.author}'
