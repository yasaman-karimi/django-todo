import uuid

from django.db import models

from apps.user.models import User


class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Todo(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    input = models.TextField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    finished_at = models.DateField(auto_now_add=True)
    done = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(default=1)
    hashtag = models.ManyToManyField(Hashtag, blank=True, related_name="todos")

    def __str__(self) -> str:
        return self.input

    def update_hashtags(self, hashtags: list[str]):
        hashtags_list = []
        for hashtag in hashtags:
            hashtag_obj, created = Hashtag.objects.get_or_create(name=hashtag)
            hashtags_list.append(hashtag_obj)
        self.hashtag.set(hashtags_list)
