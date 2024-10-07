# Generated by Django 5.1 on 2024-08-13 13:47

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Hashtag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Todo",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("input", models.TextField(max_length=100)),
                ("created_at", models.DateField(auto_now_add=True)),
                ("finished_at", models.DateField(auto_now_add=True)),
                ("done", models.BooleanField(default=False)),
                ("priority", models.PositiveSmallIntegerField(default=1)),
                ("hashtag", models.ManyToManyField(blank=True, to="todo.hashtag")),
            ],
        ),
    ]
