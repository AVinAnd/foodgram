from django.db import models
from django.core.validators import MinValueValidator

from core.models import Tag, Ingredient
from users.models import User


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор'
    )
    name = models.CharField(max_length=200, verbose_name='название')
    image = models.ImageField(
        upload_to='core/images/',
        verbose_name='изображение'
    )
    text = models.TextField(verbose_name='описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='дата публикации'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель связи ингредиента с рецептом"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_in_recipes',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes_with_ingredient',
        verbose_name='ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='количество'
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_ingredient_in_recipe')
        ]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}'


class Favorite(models.Model):
    """Модель избранного"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorite',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель списка покупок"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'список покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} - {self.recipe}'
