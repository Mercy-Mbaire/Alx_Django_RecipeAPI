from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'categories', views.CategoryViewSet, basename='category')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', include(router.urls)),
]
