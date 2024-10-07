from ninja import NinjaAPI
from ninja_apikey.security import APIKeyAuth

from apps.todo.api import router as todo_router
from apps.user.api import router as user_router

api = NinjaAPI(auth=APIKeyAuth())

api.add_router("/todos/", todo_router)
api.add_router("/users/", user_router)
