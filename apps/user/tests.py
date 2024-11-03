import pytest
from django.test.client import Client
from ninja_apikey.models import APIKey

from apps.user.models import User
from apps.user.schema import UserSignIn, UserUpdateIn


@pytest.mark.django_db
class TestSignupEndpoint:
    USER_DATA = {
        "username": "user1",
        "email": "emailExample@gmail.com",
        "password": "1234567890",
    }

    def test_successful_signup(self, client: Client):

        response = client.post(
            "/api/users/", self.USER_DATA, content_type="application/json"
        )
        assert response.status_code == 200

    def test_email_already_registered(self, client: Client):
        response = client.post(
            "/api/users/", self.USER_DATA, content_type="application/json"
        )
        assert response.status_code == 200

        another_user_data = self.USER_DATA.copy()
        another_user_data["username"] = "user2"
        response = client.post(
            "/api/users/", another_user_data, content_type="application/json"
        )

        assert response.status_code == 409

    def test_username_already_registered(self, client: Client):
        response = client.post(
            "/api/users/", self.USER_DATA, content_type="application/json"
        )
        assert response.status_code == 200

        another_user_data = self.USER_DATA.copy()
        another_user_data["email"] = "another_email_example@gmail.com"
        response = client.post(
            "/api/users/", another_user_data, content_type="application/json"
        )

        assert response.status_code == 409

    def test_missing_required_fields(self, client: Client):
        response = client.post("/api/users/", {})
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginEndpoint:

    def test_successful_login(self, client: Client, user):

        user_info = UserSignIn(username="user", password="12345678")
        response = client.post(
            "/api/users/login", user_info.dict(), content_type="application/json"
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["username"] == user.username
        assert data["email"] == user.email

    def test_failed_login(self, client: Client, user):
        user_info = UserSignIn(username=user.username, password="wrongpassword")
        response = client.post(
            "/api/users/login", user_info.dict(), content_type="application/json"
        )

        assert response.status_code == 401

    def test_missing_credentials(self, client, user):
        response = client.post("/api/users/login", {})

        assert response.status_code == 400

    def test_login_without_password(self, client: Client, user):
        user_info = UserSignIn(username=user.username, password="")
        response = client.post(
            "/api/users/login", user_info.dict(), content_type="application/json"
        )

        assert response.status_code == 401


@pytest.mark.django_db
class TestLogoutEndpoint:

    def test_logout_successful(self, client: Client, user: User, api_key: str):
        client.force_login(user)
        response = client.post(
            "/api/users/logout",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json() == {"message": "successful"}
        prefix = api_key.split(".", maxsplit=1)[0]
        assert not APIKey.objects.filter(prefix=prefix).exists()

    def test_logout_unauthorized_anonymous(self, client: Client):
        response = client.post("/api/users/logout", content_type="application/json")
        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}

    def test_logout_no_api_key(self, client: Client, user):
        client.force_login(user)
        response = client.post(
            "/api/users/logout",
            headers={"X-API-Key": ""},
            content_type="application/json",
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}

    def test_logout_invalid_api_key_format(self, client: Client, user, api_key):
        client.force_login(user)
        response = client.post(
            "/api/users/logout",
            headers={"X-API-Key": f"{api_key}invalidtoken"},
            content_type="application/json",
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.django_db
class TestUpdateEndpoint:
    def test_user_update_success(self, client: Client, user, api_key):
        client.force_login(user)

        update_data = UserUpdateIn(
            email="new_email@example.com",
            first_name="NewFirstName",
            last_name="NewLastName",
            username="newusername",
            password="newpassword123",
        )

        response = client.patch(
            "/api/users/",
            update_data.dict(),
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email == "new_email@example.com"
        assert user.first_name == "NewFirstName"
        assert user.last_name == "NewLastName"
        assert user.username == "newusername"
        assert user.check_password("newpassword123")

    def test_user_update_user_not_found(self, client: Client):

        update_data = UserUpdateIn(
            email="email@example.com",
            first_name="FirstName",
            last_name="LastName",
            username="username",
            password="password",
        )

        response = client.patch(
            "/api/users/",
            update_data.dict(),
            kwargs={"id": 999},
            content_type="application/json",
        )

        assert response.status_code == 401

    def test_user_update_username_conflict(self, client: Client, user, api_key):
        client.force_login(user)
        another_user = User.objects.create(
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        update_data = UserUpdateIn(
            username=another_user.username,
            password=user.password,
            email=user.email,
        )

        response = client.patch(
            "/api/users/",
            update_data.dict(),
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 409
        assert response.json() == {"message": "Username or email already exists."}
