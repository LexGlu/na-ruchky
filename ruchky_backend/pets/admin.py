from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ruchky_backend.pets.models import Pet, PetListing


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """
    Admin for managing pets.
    """

    list_display = (
        "name",
        "species",
        "breed",
        "owner",
        "created_at",
        "image_tag",
    )
    list_filter = ("species", "created_at")
    search_fields = ("id", "name", "breed", "owner__email")

    readonly_fields = ("id",)

    def image_tag(self, obj):
        content = (
            f'<img src="{obj.profile_picture.url}" style="max-height: 35px; width: 35px; border-radius: 50%;" />'
            if obj.profile_picture
            else "-"
        )

        return format_html(
            f'<div style="width: 100%; text-align: center;">{content}</div>'
        )

    image_tag.short_description = _("Profile Picture")


@admin.register(PetListing)
class PetListingAdmin(admin.ModelAdmin):
    """
    Admin for managing pet listings.
    """

    list_display = ("id", "pet", "status", "price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = (
        "pet__name",
        "pet__breed",
        "pet__owner__email",
        "pet__owner__first_name",
        "pet__owner__last_name",
    )
    readonly_fields = ("views_count",)
