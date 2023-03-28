from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status, pagination, exceptions, filters
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)

from core.models import Tag, Ingredient
from core.permissions import (UserPermission, RecipePermission)
from core.filters import RecipeFilter
from recipes.models import Recipe, IngredientInRecipe, Favorite, ShoppingCart
from users.models import User, Subscribe
from .mixins import (ListRetrieveCreateViewSet, )
from .serializers import (TagSerializer, IngredientSerializer, UserSerializer,
                          CreateUserSerializer, SetPasswordSerializer,
                          RecipeSerializer, CreateRecipeSerializer,
                          AddRecipeSerializer, AddUserSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов, разрешает только безопасные запросы"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингредиентов, разрешает только безопасные запросы"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class UserViewSet(ListRetrieveCreateViewSet):
    """Вьюсет для пользователей, разрешает GET и POST запросы"""
    queryset = User.objects.all()
    permission_classes = (UserPermission,)

    def get_serializer_class(self):
        """Указывает какой сериализатор используется
        в зависимости от типа запроса"""
        if self.request.method == 'POST':
            return self.serializer_class or CreateUserSerializer

        return self.serializer_class or UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        username = serializer.validated_data.get('username')
        user = self.queryset.get(username=username)
        user.set_password(serializer.validated_data.get('password'))
        user.save()
        return Response(serializer.data)

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Возвращает информацию об авторе запроса"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(methods=['post'], detail=False,
            serializer_class=SetPasswordSerializer,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """Меняет пароль пользователя"""
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        if not user.check_password(
                serializer.validated_data.get('current_password')):
            raise exceptions.ValidationError('Введен не верный пароль')

        elif user.check_password(
                serializer.validated_data.get('new_password')):
            raise exceptions.ValidationError(
                'Новый пароль должен отличаться от старого')

        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response('Пароль успешно изменен',
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            serializer_class=AddUserSerializer,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, pk):
        """Подписывается на пользователя или отписывается от него"""
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

    @action(methods=['get'], detail=False, serializer_class=AddUserSerializer,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Возвращает всех пользователей, на которых подписан автор запроса"""
        subscriptions = request.user.subscribers.all()
        authors = [sub.author for sub in subscriptions]
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов, разрешает все виды запросов"""
    queryset = Recipe.objects.all()
    permission_classes = (RecipePermission,)
    filter_backends = (DjangoFilterBackend,)
   # filterset_fields = ('author', 'tags', )
    #filterset_fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        """Указывает какой сериализатор используется
        в зависимости от типа запроса"""
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return self.serializer_class or CreateRecipeSerializer

        return self.serializer_class or RecipeSerializer

    @action(methods=['post', 'delete'], detail=True,
            serializer_class=AddRecipeSerializer,
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Добавляет рецепт в избранное или убирает из него"""
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
            serializer_class=AddRecipeSerializer,
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавляет рецепт в список покупок или убирает из него"""
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

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
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
