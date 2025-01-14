from django.contrib import admin
from ruchky_backend.pets.models import Pet, PetListing


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    """
    Admin for managing pets.
    """

    list_display = ("id", "name", "species", "breed", "owner", "created_at")
    list_filter = ("species", "created_at")
    search_fields = ("name", "breed", "owner__email")


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
