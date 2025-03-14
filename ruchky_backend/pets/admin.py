from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ruchky_backend.pets.models import Breed, Pet, PetListing, PetImage, PetSocialLink


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


class PetSocialLinkInline(admin.TabularInline):
    """
    Inline admin for pet social links.
    """

    model = PetSocialLink
    extra = 1
    fields = ("platform", "url")


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    """
    Admin for managing breeds.
    """

    list_display = (
        "name",
        "species",
        "origin",
        "life_span",
        "weight",
        "is_active",
        "image_preview",
    )
    list_filter = ("species", "is_active", "origin")
    search_fields = ("name", "description", "origin", "life_span", "weight")
    fieldsets = (
        (None, {"fields": ("name", "species", "description", "origin", "is_active")}),
        (_("Physical Attributes"), {"fields": ("life_span", "weight")}),
        (_("Image"), {"fields": ("image", "image_preview_large")}),
    )
    readonly_fields = ("image_preview_large",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = _("Preview")

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.image.url,
            )
        return "-"

    image_preview_large.short_description = _("Image Preview")


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """
    Admin for managing pets.
    """

    list_display = (
        "name",
        "species",
        "breed_display",
        "owner",
        "created_at",
        "image_tag",
    )
    list_filter = ("species", "breed", "created_at", "is_vaccinated")
    search_fields = ("id", "name", "breed__name", "owner__email")

    readonly_fields = ("id", "image_tag_large")
    inlines = [PetImageInline, PetSocialLinkInline]
    autocomplete_fields = ["breed"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "species",
                    "breed",
                    "sex",
                    "birth_date",
                    "location",
                )
            },
        ),
        (
            _("Ownership & Description"),
            {
                "fields": (
                    "owner",
                    "short_description",
                    "description",
                    "health",
                    "is_vaccinated",
                )
            },
        ),
        (_("Profile Picture"), {"fields": ("profile_picture", "image_tag_large")}),
    )

    def breed_display(self, obj):
        """Display breed name from either the breed model or custom field"""
        if obj.breed:
            return obj.breed.name
        return "-"

    breed_display.short_description = _("Breed")

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
