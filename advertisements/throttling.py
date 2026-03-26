from rest_framework.throttling import SimpleRateThrottle


class AnonRateThrottle(SimpleRateThrottle):
    """Лимит для неавторизованных пользователей: 10 запросов в минуту"""
    scope = 'anon'
    
    def get_rate(self):
        return '10/min'
    
    def allow_request(self, request, view):
        # Если пользователь авторизован, пропускаем (используем другой throttle)
        if request.user and request.user.is_authenticated:
            return True
        return super().allow_request(request, view)


class UserRateThrottle(SimpleRateThrottle):
    """Лимит для авторизованных пользователей: 20 запросов в минуту"""
    scope = 'user'
    
    def get_rate(self):
        return '20/min'
    
    def get_cache_key(self, request, view):
        # Используем ID пользователя для ключа кэша
        if request.user.is_authenticated:
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.user.pk
            }
        return None
