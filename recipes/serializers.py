from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Recipe, Category, Ingredient

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity']

class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    ingredients_list = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'category', 'title', 'description', 'ingredients', 'instructions', 'prep_time', 'cook_time', 'servings', 'created_at', 'updated_at', 'ingredients_list']

    def validate_cook_time(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cooking time must be greater than 0.")
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients_list', [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients_list', None)
        instance = super().update(instance, validated_data)

        if ingredients_data is not None:
            # Simple approach: clear existing and recreate
            instance.ingredients_list.all().delete()
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=instance, **ingredient_data)
        
        return instance


