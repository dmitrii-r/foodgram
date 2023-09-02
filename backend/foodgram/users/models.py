from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """
    Кастомная модель пользователя.
    """
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Логин',
        max_length=settings.NAME_MAX_LENGTH,
        unique=True,
        validators=(UnicodeUsernameValidator(), )
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.NAME_MAX_LENGTH,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-id']

    def __str__(self) -> str:
        return f'{self.username}'


class Subscriptions(models.Model):
    """Подписки пользователей на авторов."""
    user = models.ForeignKey(
        to=User,
        verbose_name='Подписчик',
        help_text='Пользователь, который подписывается',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    author = models.ForeignKey(
        to=User,
        verbose_name='Автор',
        help_text='Пользователь, на которого подписываются',
        on_delete=models.CASCADE,
        related_name='signed',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_self_subscription'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
