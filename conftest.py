import pytest

from apps.user.models import User


@pytest.fixture
def user():
    return User.objects.create_user(
        username="user", email="useremail@example.com", password="12345678"
    )
