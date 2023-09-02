import webcolors
from django.contrib import admin
from django.contrib.admin import display, site

from recipes.models import (Favorites, Ingredient, IngredientAmountInRecipe,
                            Recipe, ShoppingCart, Tag)

site.site_header = "Администрирование Foodgram"
EMPTY_VALUE_DISPLAY = '-пусто-'


class IngredientAmountInline(admin.TabularInline):
    """Инлайн меню для ингредиентов."""
    model = IngredientAmountInRecipe
    min_num = 1
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для тегов."""
    list_display = ('name', 'color_name')
    empty_value_display = EMPTY_VALUE_DISPLAY

    @display(description='Цвет')
    def color_name(self, obj: Tag) -> str:
        """Отображение имени цвета."""
        try:
            color_name = webcolors.hex_to_name(obj.color)
        except ValueError:
            return 'неизвестный цвет'
        return color_name


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(IngredientAmountInRecipe)
class IngredientAmountInRecipeAdmin(admin.ModelAdmin):
    """Админка для ингредиентов из рецептов, с указанием количества."""
    list_filter = ('recipe',)
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""
    list_display = ('name', 'author', 'in_favorites')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('in_favorites',)
    inlines = (IngredientAmountInline,)
    empty_value_display = EMPTY_VALUE_DISPLAY

    @admin.display(description="В избранном")
    def in_favorites(self, obj: Recipe) -> int:
        """Считает количество рецептов в избранном."""
        return obj.favorites.count()


admin.site.register(ShoppingCart)
admin.site.register(Favorites)
