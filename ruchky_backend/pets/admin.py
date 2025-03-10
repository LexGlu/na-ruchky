from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ruchky_backend.pets.models import Pet, PetListing, PetImage


class PetImageInline(admin.TabularInline):
    """
    Inline admin for pet images.
    """

    model = PetImage
    extra = 1
    fields = ("image", "order", "caption", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = _("Preview")


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

    readonly_fields = ("id", "image_tag_large")
    inlines = [PetImageInline]

    def image_tag(self, obj):
        content = (
            f'<img src="{obj.profile_picture.image.url}" style="max-height: 35px; width: 35px; border-radius: 50%;" />'
            if obj.profile_picture
            else "-"
        )

        return format_html(
            f'<div style="width: 100%; text-align: center;">{content}</div>'
        )

    image_tag.short_description = _("Profile Picture")

    def image_tag_large(self, obj):
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.profile_picture.image.url,
            )
        return "-"

    image_tag_large.short_description = _("Profile Picture Preview")


@admin.register(PetImage)
class PetImageAdmin(admin.ModelAdmin):
    """
    Admin for managing pet images.
    """

    list_display = ("pet", "order", "image_preview", "created_at")
    list_filter = ("pet__species", "created_at")
    search_fields = ("pet__name", "pet__breed", "caption")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = _("Preview")


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
