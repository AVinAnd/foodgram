from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, mixins, status, permissions, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Tag, Ingredient
from recipes.models import Recipe, IngredientInRecipe, Favorite, ShoppingCart
from users.models import User, Subscribe
from .mixins import (ListRetrieveCreateViewSet, )
from .serializers import (TagSerializer, IngredientSerializer, UserSerializer,
                          CreateUserSerializer, SetPasswordSerializer,
                          RecipeSerializer, CreateRecipeSerializer,
                          AddRecipeSerializer, AddUserSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class UserViewSet(ListRetrieveCreateViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.serializer_class or CreateUserSerializer

        return self.serializer_class or UserSerializer

    @action(methods=['get'], detail=False)
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False,
            serializer_class=SetPasswordSerializer)
    def set_password(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if not user.check_password(serializer.validated_data.get('current_password')):
            return Response('Введен не верный пароль', status=status.HTTP_400_BAD_REQUEST)
        elif user.check_password(serializer.validated_data.get('new_password')):
            return Response('Новый пароль должен отличаться от старого', status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response('Пароль успешно изменен', status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            serializer_class=AddUserSerializer)
    def subscribe(self, request, pk):
        author = self.queryset.get(id=pk)
        if author == request.user:
            return Response('Нельзя подписаться на самого себя',
                            status=status.HTTP_400_BAD_REQUEST)

        subscribe = Subscribe.objects.filter(subscriber=request.user,
                                             author=author)
        if request.method == 'DELETE':
            if not subscribe:
                return Response('Вы не подписаны на этого пользователя',
                                status=status.HTTP_400_BAD_REQUEST)

            subscribe.delete()
            return Response('Вы успешно отписались от пользователя',
                            status=status.HTTP_204_NO_CONTENT)

        if subscribe:
            return Response('Вы уже подписаны на этого пользователя',
                            status=status.HTTP_400_BAD_REQUEST)

        Subscribe.objects.create(subscriber=request.user, author=author)
        serializer = self.get_serializer(author)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, serializer_class=AddUserSerializer)
    def subscriptions(self, request):
        subscriptions = request.user.subscribers.all()
        authors = [sub.author for sub in subscriptions]
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return self.serializer_class or CreateRecipeSerializer

        return self.serializer_class or RecipeSerializer

    @action(methods=['post', 'delete'], detail=True,
            serializer_class=AddRecipeSerializer)
    def favorite(self, request, pk):
        recipe = self.queryset.get(id=pk)
        favorite = Favorite.objects.filter(user=request.user, recipe=recipe)
        if request.method == 'DELETE':
            if not favorite:
                return Response('В избранном данного рецепта нет',
                                status=status.HTTP_400_BAD_REQUEST)

            favorite.delete()
            return Response('Рецепт успешно удален из избранного',
                            status=status.HTTP_204_NO_CONTENT)

        if favorite:
            return Response('Рецепт уже добавлен в избранное',
                            status=status.HTTP_400_BAD_REQUEST)

        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True,
            serializer_class=AddRecipeSerializer)
    def shopping_cart(self, request, pk):
        recipe = self.queryset.get(id=pk)
        shopping_cart = ShoppingCart.objects.filter(user=request.user, recipe=recipe)
        if request.method == 'DELETE':
            if not shopping_cart:
                return Response('В списке покупок данного рецепта нет',
                                status=status.HTTP_400_BAD_REQUEST)

            shopping_cart.delete()
            return Response('Рецепт успешно удален из списка покупок',
                            status=status.HTTP_204_NO_CONTENT)

        if shopping_cart:
            return Response('Рецепт уже добавлен в список покупок',
                            status=status.HTTP_400_BAD_REQUEST)

        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        """Отдает пользователю список ингредиентов из его списка покупок,
        и необходимое их количество, файлом в формате .txt"""
        def add_ingredient_in_ingredient_list(
                ingredient_in_recipe: IngredientInRecipe) -> None:
            """Добавляет ингредиент в список покупок,
            суммирует количество по одинаковым ингредиентам"""
            ingredient_name = ingredient_in_recipe.ingredient.name
            measurement_unit = ingredient_in_recipe.ingredient.measurement_unit
            amount = ingredient_in_recipe.amount
            ingredient = f'{ingredient_name} ({measurement_unit})'
            if ingredient in ingredients_list:
                ingredients_list[ingredient] += amount
            else:
                ingredients_list[ingredient] = amount
            return None

        ingredients_list = {}
        recipes_in_shopping_cart = request.user.shopping_cart.all()
        for recipe in recipes_in_shopping_cart:
            ingredients_in_recipe = recipe.recipe.ingredients_in_recipes.all()
            [add_ingredient_in_ingredient_list(ingredient_in_recipe)
             for ingredient_in_recipe in ingredients_in_recipe]

        filename = 'test.txt'
        data = [f'{item} - {ingredients_list[item]}\n' for item in ingredients_list]
        response = HttpResponse(data, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = ('attachment; filename={0}'.format(filename))
        return response
