import pytest
from ninja_apikey.models import APIKey
from ninja_apikey.security import generate_key

from apps.todo.models import Todo
from apps.user.models import User


@pytest.fixture
def user():
    return User.objects.create_user(
        username="user", email="useremail@example.com", password="12345678"
    )


@pytest.fixture
def api_key(user):
    key = generate_key()
    APIKey.objects.create(
        prefix=key.prefix, user=user, hashed_key=key.hashed_key, label="test"
    )
    return f"{key.prefix}.{key.key}"


@pytest.fixture
def todo(user):
    return Todo.objects.create(owner=user, input="Buy milk", done=False, priority=1)
