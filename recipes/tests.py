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
        self.user_author = User.objects.create_user(username='author', password='password123')
        self.user_other = User.objects.create_user(username='other', password='password123')
        self.token_author = Token.objects.create(user=self.user_author)
        self.token_other = Token.objects.create(user=self.user_other)
        self.recipe = Recipe.objects.create(
            author=self.user_author,
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
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_create_sets_author(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_author.key)
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
        self.assertEqual(response.data['author'], 'author')

    def test_invalid_cook_time(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_author.key)
        data = {
            'title': 'Bad Recipe',
            'cook_time': 0,
            'prep_time': 5,
            'ingredients': 'stuff',
            'instructions': 'do things'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cook_time', response.data)

    def test_author_can_edit_own_recipe(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_author.key)
        data = {'title': 'Updated Title'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Updated Title')

    def test_non_author_cannot_edit_recipe(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token_other.key)
        data = {'title': 'Hack Title'}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.recipe.refresh_from_db()
        self.assertNotEqual(self.recipe.title, 'Hack Title')

