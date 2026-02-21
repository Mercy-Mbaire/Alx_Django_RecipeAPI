from django.contrib import admin
from .models import Recipe, Category, Ingredient

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'prep_time', 'cook_time', 'servings', 'created_at')
    search_fields = ('title', 'ingredients')

admin.site.register(Category)
admin.site.register(Ingredient)
