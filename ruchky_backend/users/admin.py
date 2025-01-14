from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from ruchky_backend.users.models import User, OrganizationProfile


class UserInline(admin.TabularInline):
    """
    Inline to show/edit multiple users under a single OrganizationProfile.
    """

    model = User
    extra = 1


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(admin.ModelAdmin):
    """
    Admin for the organization or charity profile.
    Allows inlining User records so that
    multiple staff can belong to the same organization.
    """

    list_display = ("id", "name", "is_charity", "address")
    search_fields = ("name", "address")
    inlines = [UserInline]


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
