from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Advertisement, AdvertisementStatusChoices, Favorite


class TokenInline(admin.StackedInline):
    """Inline для токенов в админке пользователя"""
    model = Token
    verbose_name = "Токен"
    verbose_name_plural = "Токены"
    max_num = 1
    can_delete = False


class CustomUserAdmin(UserAdmin):
    """Расширенная админка пользователя с токенами"""
    inlines = [TokenInline]


# Переопределяем админку пользователя
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Админка для объявлений"""
    list_display = ['id', 'title', 'status', 'creator', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'creator']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'status', 'creator')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для избранного"""
    list_display = ['id', 'user', 'advertisement', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'advertisement__title']
