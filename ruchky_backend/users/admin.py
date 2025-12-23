from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html_join
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from ruchky_backend.users.models import User, OrganizationProfile

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(OrganizationProfile)
class OrganizationProfileAdmin(ModelAdmin):
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

        user_data = [
            (reverse("admin:users_user_change", args=[user.id]), user.email)
            for user in users
        ]
        return format_html_join("<br>", '<a href="{}">{}</a>', user_data)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

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
