from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.models import User
from .views import (TagViewSet, IngredientViewSet, UserViewSet, RecipeViewSet)

app_name = 'api'

users_router_v1 = DefaultRouter()
users_router_v1.register(r'', UserViewSet)

recipes_router_v1 = DefaultRouter()
recipes_router_v1.register(r'', RecipeViewSet)
#api_router_v1.register(r'recipes/download_shopping_cart', ShoppingCartViewSet)

ingredients_router_v1 = DefaultRouter()
ingredients_router_v1.register(r'', IngredientViewSet)

tags_router_v1 = DefaultRouter()
tags_router_v1.register(r'', TagViewSet)

urlpatterns = [
    path(r'auth/token/login/', TokenCreateView.as_view(), name='login'),
    path(r'auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
    path(r'users/', include(users_router_v1.urls)),
    path(r'recipes/', include(recipes_router_v1.urls)),
    path(r'ingredients/', include(ingredients_router_v1.urls)),
    path(r'tags/', include(tags_router_v1.urls)),
]
