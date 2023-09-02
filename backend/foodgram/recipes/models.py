from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.DESCRIPTION_MAX_LENGTH,
        unique=True,
        db_index=True,
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=settings.DESCRIPTION_MAX_LENGTH,
        validators=(
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
                message='Введите цвет в формате HEX',
            ),
        )
    )
    slug = models.SlugField(
        verbose_name='Уникальный слаг',
        max_length=settings.DESCRIPTION_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self) -> str:
        return f'{self.name}'


class Ingredient(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.DESCRIPTION_MAX_LENGTH,
        db_index=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=settings.DESCRIPTION_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.name}'


class Recipe(models.Model):
    """Модель для рецептов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.DESCRIPTION_MAX_LENGTH,
    )
    author = models.ForeignKey(
        to=User,
        verbose_name='Автор',
        on_delete=models.SET_NULL,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(MinValueValidator(1, 'Не может быть меньше 1'),)
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
        default=None
    )
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Тэги',
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe_author'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.name}'


class IngredientAmountInRecipe(models.Model):
    """
    Модель связи ингредиентов с рецептами, с указанием количества ингредиентов.
    """
    ingredient = models.ForeignKey(
        to=Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(MinValueValidator(1, 'Не может быть меньше 1'),)
    )

    class Meta:
        verbose_name = 'Количество ингредиентов'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self) -> str:

        return (f'{self.recipe}: {self.ingredient} - {self.amount}'
                f'{self.ingredient.measurement_unit}.')


class ShoppingCart(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user}: {self.recipe}'


class Favorites(models.Model):
    """
    Модель для избранного.
    """
    user = models.ForeignKey(
        to=User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        to=Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorites'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user}: {self.recipe}'
