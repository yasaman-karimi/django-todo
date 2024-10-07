import pytest
from django.test.client import Client

from apps.user.schema import UserSignIn


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
