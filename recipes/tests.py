from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Recipe, Category

class RecipeAPITests(APITestCase):
    def setUp(self):
        self.user_author = User.objects.create_user(username='author', password='password123')
        self.user_other = User.objects.create_user(username='other', password='password123')
        self.token_author = Token.objects.create(user=self.user_author)
        self.token_other = Token.objects.create(user=self.user_other)
        
        self.category = Category.objects.create(name='Main Course', description='Dinner recipes')
        
        self.recipe = Recipe.objects.create(
            author=self.user_author,
            category=self.category,
            title='Test Recipe',
            description='Test Description',
            instructions='Step 1, Step 2',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        self.list_url = reverse('recipe-list')
        self.detail_url = reverse('recipe-detail', kwargs={'pk': self.recipe.pk})

    def test_register_user(self):
        url = reverse('register')
        data = {'username': 'newuser', 'email': 'new@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)

    def test_unauthenticated_read(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_author.key)
        data = {
            'title': 'New Recipe',
            'description': 'Description',
            'ingredients': 'Ingredients',
            'instructions': 'Instructions',
            'prep_time': 5,
            'cook_time': 5,
            'servings': 1,
            'category': self.category.id,
            'ingredients': [
                {'name': 'Water', 'quantity': '1 liter'},
                {'name': 'Salt', 'quantity': '1 pinch'}
            ]
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], 'author')
        self.assertEqual(len(response.data['ingredients']), 2)

    def test_author_can_update_ingredients(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_author.key)
        data = {
            'ingredients': [
                {'name': 'New Ingredient', 'quantity': '100g'}
            ]
        }
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['ingredients']), 1)
        self.assertEqual(response.data['ingredients'][0]['name'], 'New Ingredient')

    def test_is_author_or_read_only(self):
        # Non-author tries to update
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_other.key)
        data = {'title': 'Hacked!'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_category_api(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filtering(self):
        # Filter by category
        response = self.client.get(self.list_url, {'category': self.category.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF might return paginated results or a simple list. Assuming simple list based on current settings.
        self.assertEqual(len(response.data), 1)

        # Filter by cook_time
        response = self.client.get(self.list_url, {'cook_time': 20})
        self.assertEqual(len(response.data), 1)

    def test_search(self):
        # Search by title
        response = self.client.get(self.list_url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Search by description
        response = self.client.get(self.list_url, {'search': 'Description'})
        self.assertEqual(len(response.data), 1)

    def test_favorites(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_other.key)
        
        # Add to favorites
        favorite_url = reverse('recipe-favorite', kwargs={'pk': self.recipe.pk})
        response = self.client.post(favorite_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check if favorited (is_favorite field in recipe detail)
        response = self.client.get(self.detail_url)
        self.assertTrue(response.data['is_favorite'])

        # Unfavorite
        unfavorite_url = reverse('recipe-unfavorite', kwargs={'pk': self.recipe.pk})
        response = self.client.delete(unfavorite_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if unfavorited
        response = self.client.get(self.detail_url)
        self.assertFalse(response.data['is_favorite'])
