from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from ninja import NinjaAPI
from ninja_apikey.models import APIKey
from ninja_apikey.security import APIKeyAuth

from apps.todo.api import router as todo_router
from apps.user.api import router as user_router


class CustomApiKeyAuth(APIKeyAuth):
    def authenticate(self, request, key):
        user = super().authenticate(request, key)
        if user:
            api_key = key.split(".")
            prefix = api_key[0]
            try:
                user_api_key = APIKey.objects.get(prefix=prefix)
                expiration_days = getattr(settings, "API_KEY_EXPIRATION_DAYS", 30)
                user_api_key.expires_at = timezone.now() + timedelta(
                    days=expiration_days
                )
                user_api_key.save()
            except (APIKey.DoesNotExist, ValueError):
                return False
        return user


api = NinjaAPI(auth=CustomApiKeyAuth())

api.add_router("/todos/", todo_router)
api.add_router("/users/", user_router)
