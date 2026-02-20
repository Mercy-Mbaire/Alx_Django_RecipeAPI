from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Recipe

class AuthTests(APITestCase):
    def test_register_user(self):
        """
        Ensure we can register a new user.
        """
        url = reverse('register')
        data = {'username': 'testuser', 'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('token' in response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_login_user(self):
        """
        Ensure we can login and get a token.
        """
        user = User.objects.create_user(username='testuser', password='password123')
        url = reverse('api_token_auth')
        data = {'username': 'testuser', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in response.data)

class RecipePermissionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            ingredients='Ingredient 1, Ingredient 2',
            instructions='Step 1, Step 2',
            prep_time=10,
            cook_time=20,
            servings=4
        )
        self.list_url = reverse('recipe-list')
        self.detail_url = reverse('recipe-detail', kwargs={'pk': self.recipe.pk})

    def test_unauthenticated_read_list(self):
        """
        Ensure unauthenticated users can read the recipe list.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_read_detail(self):
        """
        Ensure unauthenticated users can read recipe detail.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_create(self):
        """
        Ensure unauthenticated users CANNOT create recipes.
        """
        data = {
            'title': 'New Recipe',
            'description': 'Description',
            'ingredients': 'Ingredients',
            'instructions': 'Instructions',
            'prep_time': 5,
            'cook_time': 5,
            'servings': 1
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create(self):
        """
        Ensure authenticated users CAN create recipes.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        data = {
            'title': 'New Recipe',
            'description': 'Description',
            'ingredients': 'Ingredients',
            'instructions': 'Instructions',
            'prep_time': 5,
            'cook_time': 5,
            'servings': 1
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
