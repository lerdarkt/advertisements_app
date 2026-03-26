from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class AdvertisementStatusChoices(models.TextChoices):
    """Статусы объявления"""
    OPEN = "OPEN", "Открыто"
    CLOSED = "CLOSED", "Закрыто"
    DRAFT = "DRAFT", "Черновик"


class Advertisement(models.Model):
    """Модель объявления"""
    title = models.TextField(verbose_name="Название")
    description = models.TextField(default='', verbose_name="Описание")
    status = models.TextField(
        choices=AdvertisementStatusChoices.choices,
        default=AdvertisementStatusChoices.OPEN,
        verbose_name="Статус"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Создатель"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def clean(self):
        """Валидация модели"""
        if self.status == AdvertisementStatusChoices.OPEN:
            # Проверяем, что у пользователя не больше 10 открытых объявлений
            open_ads_count = Advertisement.objects.filter(
                creator=self.creator,
                status=AdvertisementStatusChoices.OPEN
            ).count()
            
            # Если это существующее объявление и оно меняет статус, исключаем его из подсчета
            if self.pk:
                current_ad = Advertisement.objects.get(pk=self.pk)
                if current_ad.status == AdvertisementStatusChoices.OPEN:
                    open_ads_count -= 1
            
            if open_ads_count >= 10:
                raise ValidationError(
                    f"У пользователя {self.creator} уже есть 10 открытых объявлений"
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Favorite(models.Model):
    """Модель избранного (дополнительное задание)"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Пользователь"
    )
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name="Объявление"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        unique_together = ['user', 'advertisement']  # Пользователь не может добавить одно объявление дважды
    
    def __str__(self):
        return f"{self.user} - {self.advertisement}"
    
    def clean(self):
        """Валидация: автор не может добавить свое объявление в избранное"""
        if self.user == self.advertisement.creator:
            raise ValidationError("Нельзя добавить свое объявление в избранное")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
