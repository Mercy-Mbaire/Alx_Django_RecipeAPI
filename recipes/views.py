from rest_framework import status, generics, permissions, viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from .serializers import UserSerializer, RecipeSerializer, CategorySerializer, TagSerializer, TagTypeSerializer
from django.contrib.auth.models import User
from .models import Recipe, Category, Tag, TagType, Favorite
from .permissions import IsAuthorOrReadOnly

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TagTypeViewSet(viewsets.ModelViewSet):
    queryset = TagType.objects.all()
    serializer_class = TagTypeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'cook_time', 'author']
    search_fields = ['title', 'ingredients__name', 'description']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if created:
            return Response({'status': 'recipe favorited'}, status=status.HTTP_201_CREATED)
        return Response({'status': 'recipe already favorited'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAuthenticated])
    def unfavorite(self, request, pk=None):
        recipe = self.get_object()
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response({'status': 'recipe unfavorited'}, status=status.HTTP_204_NO_CONTENT)

