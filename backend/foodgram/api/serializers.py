from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from api.fields import Base64ImageField
from recipes.models import Ingredient, IngredientAmountInRecipe, Recipe, Tag

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с кастомной моделью пользователей."""
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, author: User) -> bool:
        """
        Проверка подписки пользователя.
        Проверяет подписан ли текущий пользователь на просматриваемого.
        """
        user = self.context['request'].user

        return (user.is_authenticated
                and user.subscriber.filter(author=author).exists())


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientAmountInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор связанной модели для ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmountInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountInRecipeSerializer(many=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, recipe: Recipe) -> bool:
        """Проверяет находится ли рецепт в избранном."""
        user = self.context['request'].user

        return (user.is_authenticated
                and user.favorites.filter(recipe=recipe).exists())

    def get_is_in_shopping_cart(self, recipe: Recipe) -> bool:
        """Проверяет находится ли рецепт в корзине."""
        user = self.context['request'].user

        return (user.is_authenticated
                and user.shopping_cart.filter(recipe=recipe).exists())

    @staticmethod
    def _create_ingredients(ingredients: dict, recipe: Recipe) -> None:
        """Создает список ингредиентов для рецептов."""
        for ingredient_dict in ingredients:
            ingredient = ingredient_dict['ingredient']['id']
            amount = ingredient_dict['amount']
            IngredientAmountInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

    def create(self, validated_data: dict) -> Recipe:
        """Создает рецепт."""
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self._create_ingredients(ingredients, recipe)

        return recipe

    def update(self, recipe: Recipe, validated_data: dict) -> Recipe:
        """Обновляет рецепт."""

        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            recipe.tags.clear()
            recipe.tags.set(tags)

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            IngredientAmountInRecipe.objects.filter(recipe=recipe).delete()
            self._create_ingredients(ingredients, recipe)

        recipe.name = validated_data.get('name', recipe.name)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.text = validated_data.get('text', recipe.text)
        recipe.cooking_time = validated_data.get('cooking_time',
                                                 recipe.cooking_time)
        recipe.save()

        return recipe

    def to_representation(self, recipe: Recipe) -> Recipe:
        """Предоставляет рецепт в необходимом для выдачи формате."""
        self.fields['tags'] = TagSerializer(many=True)
        return super().to_representation(recipe)


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов. Компактная версия"""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""

    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (CustomUserSerializer.Meta.fields
                  + ('recipes', 'recipes_count'))

    @staticmethod
    def get_recipes(obj: User) -> Recipe:
        """Показывает авторские рецепты пользователя."""
        return ShortRecipeSerializer(obj.recipes.all(), many=True).data

    @staticmethod
    def get_recipes_count(obj: User) -> int:
        """Показывает количество авторских рецептов пользователя."""
        return obj.recipes.all().count()
