from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from ruchky_backend.users.models import User, OrganizationProfile


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    """
    Admin for the organization or charity profile with read-only user display.
    """

    list_display = ("id", "name", "is_charity", "address", "get_users")
    search_fields = ("name", "address")
    readonly_fields = ("get_users",)

    @admin.display(description="Users")
    def get_users(self, obj: OrganizationProfile):
        users = obj.users.all()
        if not users:
            return "-"

        user_links = []
        for user in users:
            url = reverse("admin:users_user_change", args=[user.id])
            user_links.append(f'<a href="{url}">{user.email}</a>')
        return format_html("<br>".join(user_links))


@admin.register(User)
class CustomUserAdmin(UserAdmin):

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
        (_("Organization"), {"fields": ("organization",)}),
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
                "fields": ("email", "password1", "password2", "organization"),
            },
        ),
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "organization__is_charity",
    )
    list_display = (
        "email",
        "organization",
        "first_name",
        "last_name",
        "date_joined",
        "last_login",
        "is_staff",
    )
    search_fields = ("first_name", "last_name", "email", "phone", "organization__name")
    ordering = ("email",)
    filter_horizontal = [
        "groups",
        "user_permissions",
    ]
    readonly_fields = ("id", "date_joined", "last_login")
