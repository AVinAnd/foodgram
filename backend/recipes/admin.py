from django.contrib import admin

from recipes.models import Recipe, IngredientInRecipe, Favorite, ShoppingCart

admin.site.register(IngredientInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Модель рецептов в админке"""
    list_display = ('name', 'author', 'in_favorite')
    list_filter = ('author', 'name', 'tags')

    def in_favorite(self, obj):
        """Показывает сколько раз рецепт был добавлен в избранное"""
        count = obj.in_favorite.all().count()
        return count
