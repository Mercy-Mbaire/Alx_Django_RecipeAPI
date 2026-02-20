from django.urls import path
from . import views

urlpatterns = [
    path('', views.RecipeList.as_view(), name='recipe-list'),
    path('<int:pk>/', views.RecipeDetail.as_view(), name='recipe-detail'),
    path('register/', views.register, name='register'),
]
