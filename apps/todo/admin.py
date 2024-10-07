from django.contrib import admin

from .models import Hashtag, Todo


class TodoAdmin(admin.ModelAdmin):
    list_display = ["input", "owner"]
    readonly_fields = ("owner",)


# Register your models here.
admin.site.register(Todo, TodoAdmin)
admin.site.register(Hashtag)
