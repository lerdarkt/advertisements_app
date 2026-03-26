from rest_framework import viewsets, permissions, status, filters as drf_filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django.db.models import Q
from .models import Advertisement, AdvertisementStatusChoices, Favorite
from .serializers import AdvertisementSerializer, FavoriteSerializer
from .permissions import IsOwnerOrAdmin, IsOwnerOrAdminForDraft
from .filters import AdvertisementFilter
from .throttling import AnonRateThrottle, UserRateThrottle


class AdvertisementViewSet(viewsets.ModelViewSet):
    """ViewSet для объявлений"""
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filter_backends = [
        django_filters.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    filterset_class = AdvertisementFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    # Настройка throttling
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_queryset(self):
        """Фильтрация queryset в зависимости от статуса и пользователя"""
        user = self.request.user
        
        if user.is_authenticated:
            # Авторизованный пользователь:
            # - видит все открытые объявления
            # - видит закрытые объявления (все)
            # - видит черновики только свои
            queryset = Advertisement.objects.filter(
                Q(status=AdvertisementStatusChoices.OPEN) |
                Q(status=AdvertisementStatusChoices.CLOSED) |
                Q(status=AdvertisementStatusChoices.DRAFT, creator=user)
            )
        else:
            # Неавторизованный пользователь видит только открытые объявления
            queryset = Advertisement.objects.filter(status=AdvertisementStatusChoices.OPEN)
        
        return queryset
    
    def get_permissions(self):
        """Разные права для разных действий"""
        if self.action in ['create']:
            # Создавать могут только авторизованные пользователи
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Обновлять и удалять может только автор или админ
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            # Просматривать могут все, но с учетом статуса
            permission_classes = [permissions.AllowAny]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """При создании автоматически устанавливаем создателя"""
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """
        Добавление/удаление объявления в избранное
        POST /api/advertisements/{id}/favorite/ - добавить
        DELETE /api/advertisements/{id}/favorite/ - удалить
        """
        advertisement = self.get_object()
        user = request.user
        
        # Проверка, что автор не добавляет свое объявление
        if user == advertisement.creator:
            return Response(
                {'error': 'Нельзя добавить свое объявление в избранное'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.method == 'POST':
            # Добавляем в избранное
            favorite, created = Favorite.objects.get_or_create(
                user=user,
                advertisement=advertisement
            )
            if created:
                return Response(
                    {'message': 'Объявление добавлено в избранное'},
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    {'error': 'Объявление уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        elif request.method == 'DELETE':
            # Удаляем из избранного
            deleted, _ = Favorite.objects.filter(
                user=user,
                advertisement=advertisement
            ).delete()
            if deleted:
                return Response(
                    {'message': 'Объявление удалено из избранного'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'error': 'Объявление не найдено в избранном'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def favorites(self, request):
        """
        Получить список избранных объявлений
        GET /api/advertisements/favorites/
        """
        favorites = Favorite.objects.filter(user=request.user).select_related('advertisement')
        serializer = FavoriteSerializer(favorites, many=True, context={'request': request})
        return Response(serializer.data)
