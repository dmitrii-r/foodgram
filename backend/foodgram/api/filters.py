from typing import Any

from django.db.models import Q, QuerySet
from django.db.models.functions import Lower
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (CharFilter,
                                                   ModelMultipleChoiceFilter,
                                                   NumberFilter)
from rest_framework import filters
from rest_framework.request import Request
from rest_framework.views import APIView

from recipes.models import Recipe, Tag


class IngredientSearchFilter(filters.SearchFilter):
    """
    Фильтр для поиска по вхождению в начало названия
    и в произвольном месте, с сортировкой от первого ко второму.
    """
    search_param = 'name'

    def filter_queryset(
            self,
            request: Request,
            queryset: QuerySet,
            view: APIView
    ) -> QuerySet:
        search_terms = ''.join(self.get_search_terms(request))
        filtered_queryset = queryset.filter(
            Q(name__istartswith=search_terms) | Q(name__icontains=search_terms)
        ).extra(
            select={
                "startswith_match":
                    "CASE WHEN name ILIKE %s || '%%' THEN 0 ELSE 1 END"
            },
            select_params=[search_terms],
            order_by=["startswith_match", Lower("name")]
        )

        return filtered_queryset


class RecipeFilters(FilterSet):
    """
    Фильтрация по тегам, автору, избранному и списку покупок.
    """
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    author = CharFilter()
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(
            self,
            queryset: QuerySet,
            name: str,
            value: Any
    ) -> QuerySet:
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(
            self,
            queryset: QuerySet,
            name: str,
            value: Any
    ) -> QuerySet:
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset
