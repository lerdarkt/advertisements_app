from django_filters import rest_framework as filters
from .models import Advertisement, AdvertisementStatusChoices


class AdvertisementFilter(filters.FilterSet):
    """Фильтр для объявлений"""
    
    # Фильтрация по дате создания
    created_at = filters.DateFromToRangeFilter(
        field_name='created_at',
        label='Дата создания (диапазон)'
    )
    
    # Фильтрация по статусу
    status = filters.ChoiceFilter(
        choices=AdvertisementStatusChoices.choices,
        field_name='status'
    )
    
    class Meta:
        model = Advertisement
        fields = {
            'status': ['exact'],
            'created_at': ['gte', 'lte'],
        }
