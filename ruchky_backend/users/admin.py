from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from ruchky_backend.users import models


@admin.register(models.User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "date_joined",
        "last_login",
        "is_staff",
    )
    search_fields = ("first_name", "last_name", "email")
    ordering = ("email",)
    filter_horizontal = [
        "groups",
        "user_permissions",
    ]
    readonly_fields = ("id", "date_joined", "last_login")
