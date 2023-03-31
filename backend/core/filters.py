from django_filters import rest_framework as rf_filters
from rest_framework import filters

from recipes.models import Recipe
from core.models import Tag


class RecipeFilter(rf_filters.FilterSet):
    """Фильтры для рецептов"""
    is_favorited = rf_filters.BooleanFilter(
        label='is_favorited', method='filter_is_favorited')
    is_in_shopping_cart = rf_filters.BooleanFilter(
        label='is_in_shopping_cart', method='filter_is_in_shopping_cart')
    tags = rf_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, _, value):
        """Выводит список рецептов которые находятся или отсутствуют
        в списке избранного у пользователя"""
        recipes_in_favorite = self.request.user.favorite.all()
        recipes_id = [recipe.recipe.id for recipe in recipes_in_favorite]
        if value:
            return queryset.filter(id__in=recipes_id)

        return queryset.exclude(id__in=recipes_id)

    def filter_is_in_shopping_cart(self, queryset, _, value):
        """Выводит список рецептов которые находятся или отсутствуют
        в списке покупок у пользователя"""
        recipes_in_shopping_cart = self.request.user.shopping_cart.all()
        recipes_id = [recipe.recipe.id for recipe in recipes_in_shopping_cart]
        if value:
            return queryset.filter(id__in=recipes_id)

        return queryset.exclude(id__in=recipes_id)


class IngredientFilter(filters.SearchFilter):
    search_param = 'name'
