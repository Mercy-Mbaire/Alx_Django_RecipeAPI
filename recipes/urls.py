from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.RecipeViewSet, basename='recipe')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', include(router.urls)),
]
