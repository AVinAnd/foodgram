from django.contrib import admin
from .models import Recipe, IngredientInRecipe, Favorite, ShoppingCart

admin.site.register(Recipe)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
