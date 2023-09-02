from datetime import datetime as dt

from django.db.models import Sum

from recipes.models import IngredientAmountInRecipe, ShoppingCart


def get_shopping_list(user: str) -> str:
    """Формирует список покупок."""
    recipes = (ShoppingCart.objects.filter(user=user)
               .values('recipe__name'))
    recipes_list = (f'{recipe["recipe__name"]}\n' for recipe in recipes)
    ingredients = (IngredientAmountInRecipe.objects.filter(
        recipe__shopping_cart__user=user
    ).values('ingredient__name', 'ingredient__measurement_unit')
     .annotate(sum_amount=Sum('amount'))
     .order_by('ingredient__name'))
    ingredients_list = (
        f'{ingredient["ingredient__name"]}: '
        f'{ingredient["sum_amount"]} '
        f'{ingredient["ingredient__measurement_unit"]}.\n'
        for ingredient in ingredients
    )
    shopping_list = [
        f'Foodgram, «Продуктовый помощник»\n'
        f'Список ингредиентов для приготовления рецептов.\n\n'
        f'Подготовлен для: {user.get_full_name()}\n'
        f'Дата: {dt.now().strftime("%d/%m/%Y %H:%M")}\n\n'
        'Список покупок:\n'
        '------------------------------------------------\n'
    ]
    shopping_list.extend(ingredients_list)
    shopping_list.append(
        '------------------------------------------------\n\n'
        'Список подготовлен для рецептов:\n'
        '------------------------------------------------\n'
    )
    shopping_list.extend(recipes_list)
    shopping_list.append(
        '------------------------------------------------'
        '\n\n'
        'Приятных покупок!\nЖдем вас снова на Foodgram.'
    )
    shopping_list = ''.join(shopping_list)

    return shopping_list
