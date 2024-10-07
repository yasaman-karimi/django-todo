from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email"]
    list_per_page = 50


# Register your models here.
admin.site.register(User, UserAdmin)
