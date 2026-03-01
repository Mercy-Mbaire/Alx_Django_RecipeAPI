from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'recipes', views.RecipeViewSet, basename='recipe')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'tag-types', views.TagTypeViewSet, basename='tagtype')
router.register(r'tags', views.TagViewSet, basename='tag')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', include(router.urls)),
]
