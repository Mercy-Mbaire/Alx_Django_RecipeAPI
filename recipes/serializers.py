from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Recipe, Category, Ingredient, Tag, TagType, Favorite

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

class TagTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagType
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    tag_type = TagTypeSerializer(read_only=True)
    tag_type_id = serializers.PrimaryKeyRelatedField(
        queryset=TagType.objects.all(), source='tag_type', write_only=True
    )

    class Meta:
        model = Tag
        fields = ['id', 'name', 'tag_type', 'tag_type_id']

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity']

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe', 'created_at']
        read_only_fields = ['user', 'created_at']

class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=False, allow_null=True)
    ingredients = IngredientSerializer(many=True, required=False)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), source='tags', many=True, write_only=True, required=False
    )

    class Meta:
        model = Recipe
        fields = [
            'id', 'author', 'category', 'title', 'description', 
            'instructions', 'prep_time', 'cook_time', 'servings', 
            'tags', 'tag_ids', 'created_at', 'updated_at', 'ingredients',
            'is_favorite'
        ]

    is_favorite = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def validate_cook_time(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cooking time must be greater than 0.")
        return value

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags_data = validated_data.pop('tags', None)
        
        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ingredient_data in ingredients_data:
                Ingredient.objects.create(recipe=instance, **ingredient_data)
        
        return instance


