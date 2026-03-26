from rest_framework import serializers
from .models import Advertisement, AdvertisementStatusChoices, Favorite


class AdvertisementSerializer(serializers.ModelSerializer):
    """Сериализатор для объявлений"""
    creator = serializers.ReadOnlyField(source='creator.username')
    
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'description', 'status', 'creator', 'created_at', 'updated_at']
        read_only_fields = ['creator', 'created_at', 'updated_at']
    
    def validate_status(self, value):
        """Валидация статуса"""
        if value not in [choice[0] for choice in AdvertisementStatusChoices.choices]:
            raise serializers.ValidationError(f"Недопустимый статус: {value}")
        return value
    
    def validate(self, data):
        """Валидация данных"""
        # Проверка количества открытых объявлений
        if data.get('status') == AdvertisementStatusChoices.OPEN:
            request = self.context.get('request')
            if request and request.user:
                open_ads_count = Advertisement.objects.filter(
                    creator=request.user,
                    status=AdvertisementStatusChoices.OPEN
                ).count()
                
                # Если это обновление существующего объявления
                if self.instance:
                    if self.instance.status == AdvertisementStatusChoices.OPEN:
                        open_ads_count -= 1
                
                if open_ads_count >= 10:
                    raise serializers.ValidationError(
                        "У вас уже есть 10 открытых объявлений. Закройте одно из них, чтобы создать новое."
                    )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного"""
    advertisement = AdvertisementSerializer(read_only=True)
    advertisement_id = serializers.PrimaryKeyRelatedField(
        queryset=Advertisement.objects.all(),
        source='advertisement',
        write_only=True
    )
    
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'advertisement', 'advertisement_id', 'created_at']
        read_only_fields = ['user', 'created_at']
    
    def validate(self, data):
        """Проверка, что пользователь не добавляет свое объявление"""
        request = self.context.get('request')
        advertisement = data.get('advertisement')
        
        if request and request.user == advertisement.creator:
            raise serializers.ValidationError("Нельзя добавить свое объявление в избранное")
        
        # Проверка, что объявление уже не в избранном
        if Favorite.objects.filter(user=request.user, advertisement=advertisement).exists():
            raise serializers.ValidationError("Объявление уже в избранном")
        
        return data
