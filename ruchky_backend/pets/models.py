from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from taggit.models import GenericUUIDTaggedItemBase, TaggedItemBase

from ruchky_backend.helpers.db.models import (
    UUIDMixin,
    DateTimeMixin,
    generate_filename,
)
from ruchky_backend.helpers.storage import storage
from ruchky_backend.users.models import User


class UUIDTaggedItem(GenericUUIDTaggedItemBase, TaggedItemBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class Species(models.TextChoices):
    DOG = "dog", _("Dog")
    CAT = "cat", _("Cat")


class Sex(models.TextChoices):
    FEMALE = "f", _("Female")
    MALE = "m", _("Male")


class SocialPlatform(models.TextChoices):
    INSTAGRAM = "instagram", _("Instagram")
    TIKTOK = "tiktok", _("TikTok")
    YOUTUBE = "youtube", _("YouTube")


class Breed(UUIDMixin, DateTimeMixin):
    """
    Designed to be extended with additional fields in the future.
    """

    name = models.CharField(_("Name"), max_length=100)
    species = models.CharField(_("Species"), max_length=20, choices=Species.choices)
    description = models.TextField(_("Description"), blank=True, null=True)
    life_span = models.CharField(
        _("Life Span"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Average life span of the breed"),
    )
    weight = models.CharField(
        _("Weight"),
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Average weight of the breed"),
    )

    origin = models.CharField(_("Origin"), max_length=100, blank=True, null=True)

    image = models.ImageField(
        verbose_name=_("Breed Image"),
        upload_to=generate_filename,
        storage=storage,
        blank=True,
        null=True,
        help_text=_("Representative image of the breed"),
    )

    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("Breed")
        verbose_name_plural = _("Breeds")
        ordering = ["species", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "species"], name="unique_breed_per_species"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_species_display()})"


class Pet(UUIDMixin, DateTimeMixin):
    """
    The core pet model: includes ownership by a User (which could be
    an individual or an organization/charity).
    """

    name = models.CharField(_("Name"), max_length=100)
    species = models.CharField(_("Species"), max_length=20, choices=Species.choices)

    breed = models.ForeignKey(
        Breed,
        on_delete=models.SET_NULL,
        related_name="pets",
        verbose_name=_("Breed"),
        blank=True,
        null=True,
    )

    sex = models.CharField(_("Sex"), max_length=1, choices=Sex.choices)
    birth_date = models.DateField(_("Birth Date"))
    location = models.CharField(_("Location"), max_length=100, blank=True, null=True)
    is_vaccinated = models.BooleanField(_("Vaccinated"), default=False)

    short_description = models.TextField(_("Short Description"), blank=True, null=True)
    description = models.TextField(_("Description"), blank=True, null=True)
    health = models.TextField(_("Health"), blank=True, null=True)
    profile_picture = models.ForeignKey(
        "PetImage",
        on_delete=models.SET_NULL,
        related_name="profile_for",
        verbose_name=_("Profile Picture"),
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets",
        verbose_name=_("Owner"),
    )

    tags = TaggableManager(through=UUIDTaggedItem)

    def __str__(self) -> str:
        """Returns a formatted string representation of the pet."""
        base = f"{self.name} ({self.get_species_display()}"
        breed_name = self.get_breed_name()

        if breed_name:
            return f"{base}, {breed_name})"

        return f"{base})"

    def get_breed_name(self) -> str:
        """Returns the breed name, either from the related model or custom field"""
        return self.breed.name if self.breed else None


class PetImage(UUIDMixin, DateTimeMixin):
    """
    Model to store additional images for a pet.
    """

    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Pet"),
    )
    image = models.ImageField(
        verbose_name=_("Image"),
        upload_to=generate_filename,
        storage=storage,
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("Order in which the image appears in the gallery"),
    )
    caption = models.CharField(_("Caption"), max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("Pet Image")
        verbose_name_plural = _("Pet Images")

    def __str__(self):
        return f"{self.pet.name} - Image {self.order}"


class PetSocialLink(UUIDMixin, DateTimeMixin):
    """
    Model to store pet-specific social media links.
    One pet can have multiple social links for various platforms.
    """

    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name="social_links",
        verbose_name=_("Pet"),
    )
    platform = models.CharField(
        _("Platform"),
        max_length=20,
        choices=SocialPlatform.choices,
    )
    url = models.URLField(_("URL"), max_length=500)

    def __str__(self):
        return f"{self.pet.name} - {self.get_platform_display()}"


class ListingStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    SOLD = "sold", _("Sold")
    ADOPTED = "adopted", _("Adopted")
    EXPIRED = "expired", _("Expired")
    ARCHIVED = "archived", _("Archived")


class PetListing(UUIDMixin, DateTimeMixin):
    """
    A listing for a Pet.
    """

    pet = models.OneToOneField(
        Pet,
        on_delete=models.CASCADE,
        related_name="listing",
        verbose_name=_("Pet"),
    )
    title = models.CharField(_("Title"), max_length=100)
    status = models.CharField(
        _("Listing Status"),
        max_length=20,
        choices=ListingStatus.choices,
        default=ListingStatus.ACTIVE,
    )
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text=_("Set 0 or leave blank for free/adoption."),
    )
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Listing for {self.pet.name} [{self.get_status_display()}]"

    def is_active(self):
        return self.status == ListingStatus.ACTIVE

    def is_sold(self):
        return self.status == ListingStatus.SOLD

    def is_adopted(self):
        return self.status == ListingStatus.ADOPTED

    def is_expired(self):
        return self.status == ListingStatus.EXPIRED

    def is_archived(self):
        return self.status == ListingStatus.ARCHIVED
