from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilters
from api.paginators import LimitPageNumberPagination
from api.permissions import IsAdminOwnerOrReadOnly
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             ShortRecipeSerializer, SubscriptionSerializer,
                             TagSerializer)
from api.services import get_shopping_list
from recipes.models import Favorites, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscriptions

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для тегов.
    Получение тега или списка тегов.
    Доступно для всех пользователей.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для ингредиентов.
    Получение ингредиента или списка ингредиентов.
    Поиск по названию ингредиента.
    Доступно для всех пользователей.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для рецептов.
    Получение рецепта или списка рецептов доступно для всех пользователей.
    Фильтрация по тегам, автору, избранному и списку покупок.
    Обновление и удаление рецепта доступно только автору рецепта.
    Авторизованным пользователям доступно:
    - создание рецепта;
    - добавление, удаление рецепта из списка покупок;
    - скачивание списка ингредиентов в txt файле;
    - добавление, удаление рецепта из избранного.
    """
    queryset = (Recipe.objects.select_related('author')
                .prefetch_related('ingredients')
                .prefetch_related('tags'))
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilters
    permission_classes = [IsAdminOwnerOrReadOnly]
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request: Request, pk: int | str) -> Response:
        """Добавление, удаление рецепта из списка покупок."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShortRecipeSerializer(recipe)
        user = request.user
        recipe_in_shopping_cart = user.shopping_cart.filter(recipe=recipe)

        if request.method == 'POST' and not recipe_in_shopping_cart.exists():
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE' and recipe_in_shopping_cart.exists():
            recipe_in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            data={'error': 'Рецепт уже в списке покупок.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request: Request) -> HttpResponse:
        """Скачивание списка ингредиентов в txt файле."""
        shopping_list = get_shopping_list(user=request.user)
        filename = f'{request.user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request: Request, pk: int | str) -> Response:
        """Добавление, удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShortRecipeSerializer(recipe)
        user = request.user
        recipe_in_favorites = user.favorites.filter(recipe=recipe)

        if request.method == 'POST' and not recipe_in_favorites.exists():
            Favorites.objects.create(user=user, recipe=recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE' and recipe_in_favorites.exists():
            recipe_in_favorites.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            data={'error': 'Рецепт уже в избранном.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(DjoserUserViewSet):
    """
    Вьюсет для расширения функционала работы с пользователями.
    Зарегистрированные пользователи могут:
    - подписываться на других пользователей и удалять свою подписку;
    - просматривать список своих подписок.
    """
    pagination_class = LimitPageNumberPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request: Request, id: int | str) -> Response:
        """Подписка на авторов, удаление подписки."""
        user = request.user
        author = get_object_or_404(User, pk=id)
        subscription = user.subscriber.filter(author=author)

        if user == author:
            return Response(
                data={'error': 'Нельзя подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if not subscription.exists():
                Subscriptions.objects.create(user=user, author=author)
                self.serializer_class = SubscriptionSerializer
                serializer = self.get_serializer(author)
                return Response(data=serializer.data,
                                status=status.HTTP_201_CREATED)

            return Response(
                data={'error': 'Вы уже подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            return Response(
                data={'error': 'Вы и так не подписаны на этого автора.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request: Request) -> Response:
        """Возвращает список авторов на которых подписан пользователь."""
        user = request.user
        queryset = User.objects.filter(signed__user=user)
        subscriptions = self.paginate_queryset(queryset)
        self.serializer_class = SubscriptionSerializer
        serializer = self.get_serializer(subscriptions, many=True)

        return self.get_paginated_response(serializer.data)
