# Alx_Django_RecipeAPI

A Django REST API for managing recipes, featuring advanced filtering, search, tagging, and favorites.

## Features
- **Recipe Management**: Full CRUD operations for recipes.
- **Filtering**: Filter recipes by category, cooking time, and author.
- **Search**: Search recipes by title, ingredients, and description.
- **Tagging**: Categorize recipes with flexible tags.
- **Favorites**: Users can mark recipes as favorites and view their favorite list.

## Filtering and Search
- **Search**: `GET /recipes/?search=chicken`
- **Category Filter**: `GET /recipes/?category=1`
- **Cooking Time Filter**: `GET /recipes/?cook_time=30`
- **Author Filter**: `GET /recipes/?author=2`

## Favorites
- **Favorite a recipe**: `POST /recipes/<id>/favorite/`
- **Unfavorite a recipe**: `DELETE /recipes/<id>/unfavorite/`
- **View Favorite Status**: The `is_favorite` field in the recipe list and detail views indicates if the current user has favorited the recipe.

## Setup Instructions
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt` (or `pip install django djangorestframework django-filter`)
3. Run migrations: `python manage.py migrate`
4. Start the server: `python manage.py runserver`

## Testing
Run the tests using:
```bash
python manage.py test recipes
```
