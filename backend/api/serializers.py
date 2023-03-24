import base64

from rest_framework import serializers, exceptions, status
from django.core import serializers as django_serializer
from django.core.files.base import ContentFile

from core.models import Tag, Ingredient
from recipes.models import Recipe, IngredientInRecipe, Favorite, ShoppingCart
from users.models import User, Subscribe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        "Декодирование изображения"
        if isinstance(data, str) and data.startswith('data:image'):
            file_format, img_code = data.split(';base64,')
            ext = file_format.split('/')[-1]
            data = ContentFile(base64.b64decode(img_code), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей при безопасных запросах"""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, user):
        """Проверяет подписку автора запроса на запрашиваемого пользователя"""
        subscriber = self.context.get('request').user
        if Subscribe.objects.filter(subscriber=subscriber.id, author=user.id):
            return True
        return False


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователей"""
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class SetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('new_password', 'current_password')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_ingredients(self, recipe):
        ingredients_in_recipe = recipe.ingredients_in_recipes.all()
        return IngredientInRecipeSerializer(ingredients_in_recipe, many=True).data

    def get_is_favorited(self, recipe):
        user = self.context.get('request').user
        if Favorite.objects.filter(user=user.id, recipe=recipe.id):
            return True
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('request').user
        if ShoppingCart.objects.filter(user=user.id, recipe=recipe.id):
            return True
        return False


class CreateIngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1, write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_in_recipe = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        ingredients = [IngredientInRecipe(
            recipe=recipe,
            ingredient=ingredient.get('id'),
            amount=ingredient.get('amount')
        ) for ingredient in ingredients_in_recipe]
        IngredientInRecipe.objects.bulk_create(ingredients)
        return recipe

    def update(self, instance, validated_data):
        new_ingredients_in_recipe = validated_data.get('ingredients')
        instance.tags.set(validated_data.get('tags'))
        instance.image = validated_data.get('image')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.ingredients_in_recipes.all().delete()
        ingredients = [IngredientInRecipe(
            recipe=instance,
            ingredient=ingredient.get('id'),
            amount=ingredient.get('amount')
        ) for ingredient in new_ingredients_in_recipe]
        IngredientInRecipe.objects.bulk_create(ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        serializer = RecipeSerializer(instance, context=self.context)
        return serializer.data


class AddRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AddUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(default=True, read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, user):
        recipes = user.recipes.all()
        return AddRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, user):
        return len(user.recipes.all())
