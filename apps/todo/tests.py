from uuid import uuid4

import pytest
from django.test.client import Client

from apps.todo.models import Hashtag, Todo
from apps.user.models import User


@pytest.mark.django_db
class TestSearchEndpoint:
    def test_search_no_params(self, client: Client, user, api_key):
        client.force_login(user)
        response = client.get(
            "/api/todos/search",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_search_with_query(self, client: Client, user, api_key):
        client.force_login(user)
        Todo.objects.create(owner=user, input="Buy milk")
        Todo.objects.create(owner=user, input="Buy bread")

        response = client.get(
            "/api/todos/search",
            {"q": "milk"},
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["input"] == "Buy milk"

    def test_search_with_hashtags(self, client: Client, user, api_key):
        client.force_login(user)
        todo_with_hashtags = Todo.objects.create(owner=user, input="Buy milk")
        hashtag = Hashtag.objects.create(name="grocery")
        todo_with_hashtags.hashtag.add(hashtag)

        Todo.objects.create(owner=user, input="Buy bread")

        response = client.get(
            "/api/todos/search",
            {"hashtags": "grocery"},
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["input"] == "Buy milk"

    def test_search_with_multiple_conditions(self, client: Client, user, api_key):
        client.force_login(user)
        Todo.objects.create(owner=user, input="Buy milk")
        hashtag = Hashtag.objects.create(name="grocery")
        todo_with_hashtags = Todo.objects.create(owner=user, input="Buy bread")
        todo_with_hashtags.hashtag.add(hashtag)

        response = client.get(
            "/api/todos/search",
            {"q": "bread", "hashtags": "grocery"},
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["input"] == "Buy bread"


@pytest.mark.django_db
class TestGetTodosEndpoint:
    def test_get_todos_empty(self, client: Client, user, api_key):
        client.force_login(user)

        response = client.get(
            "/api/todos/",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_get_todos_with_data(self, client: Client, user, api_key):
        client.force_login(user)

        Todo.objects.create(owner=user, input="Buy milk")
        Todo.objects.create(owner=user, input="Buy bread")

        response = client.get(
            "/api/todos/",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert len(response.json()) == 2
        assert response.json()[0]["input"] == "Buy milk"
        assert response.json()[1]["input"] == "Buy bread"

    def test_get_todos_unauthenticated(self, client: Client):
        response = client.get("/api/todos/")

        assert response.status_code == 401


@pytest.mark.django_db
class TestCreateTodoEndpoint:

    def test_create_todo_success(self, client: Client, user, api_key):
        client.force_login(user)

        response = client.post(
            "/api/todos/",
            {"input": "Buy milk"},
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["input"] == "Buy milk"
        assert Todo.objects.filter(owner=user).count() == 1

    def test_create_todo_unauthenticated(self, client: Client):
        response = client.post("/api/todos/", {"input": "Buy milk"})

        assert response.status_code == 401

    def test_create_todo_invalid_data(self, client: Client, user, api_key):
        client.force_login(user)

        response = client.post(
            "/api/todos/",
            {"input": ""},
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json() == {"message": "input is empty"}


@pytest.mark.django_db
class TestEditTodoEndpoint:

    def test_edit_todo_success(self, client: Client, user, todo, api_key):
        client.force_login(user)
        todo_data = {"input": "Buy almond milk", "done": True, "priority": 2}
        response = client.patch(
            f"/api/todos/{todo.id}",
            todo_data,
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["input"] == "Buy almond milk"
        assert response.json()["done"] is True
        assert response.json()["priority"] == 2

        todo.refresh_from_db()
        assert todo.input == "Buy almond milk"
        assert todo.done is True
        assert todo.priority == 2

    def test_edit_todo_not_found(self, client: Client, user, api_key):
        client.force_login(user)

        response = client.patch(
            f"/api/todos/{uuid4()}",
            {"input": "Buy almond milk"},
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_edit_todo_unauthenticated(self, client: Client, todo):
        todo_data = {"input": "Buy almond milk"}
        response = client.patch(f"/api/todos/{todo.id}", todo_data)

        assert response.status_code == 401


@pytest.mark.django_db
class TestDeleteTodoEndpoint:
    def test_delete_todo_success(self, client: Client, user, todo, api_key):
        client.force_login(user)

        response = client.delete(
            f"/api/todos/{todo.id}",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["message"] == "deleted"

        assert Todo.objects.filter(id=todo.id).count() == 0

    def test_delete_todo_not_found(self, client: Client, user, api_key):
        client.force_login(user)

        response = client.delete(
            f"/api/todos/{uuid4()}",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_delete_todo_unauthenticated(self, client: Client, todo):
        response = client.delete(f"/api/todos/{todo.id}")

        assert response.status_code == 401

    def test_delete_todo_not_owned(self, client: Client, user, api_key):
        other_user = User.objects.create(username="otheruser", password="password")
        todo = Todo.objects.create(
            owner=other_user, input="Buy bread", done=False, priority=1
        )

        client.force_login(user)

        response = client.delete(
            f"/api/todos/{todo.id}",
            headers={"X-API-Key": api_key},
            content_type="application/json",
        )

        assert response.status_code == 404
