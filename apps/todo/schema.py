from uuid import UUID

from ninja import Schema

from .models import Todo


class TodoOut(Schema):
    id: UUID
    input: str
    done: bool = False
    priority: int = 1
    hashtags: list[str] = None

    @staticmethod
    def resolve_hashtags(obj: Todo):
        return obj.hashtag.all().values_list("name", flat=True)


class TodoIn(Schema):
    input: str
    done: bool = False
    priority: int = 1
    hashtag: list[str] | None = None


class TodoUpdateIn(Schema):
    input: str | None = None
    done: bool | None = None
    priority: int | None = None
    hashtag: list[str] | None = None


class Message(Schema):
    message: str
