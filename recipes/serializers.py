from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Recipe

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

class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Recipe
        fields = ['id', 'author', 'title', 'description', 'ingredients', 'instructions', 'prep_time', 'cook_time', 'servings', 'created_at', 'updated_at']

    def validate_cook_time(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cooking time must be greater than 0.")
        return value

