from django.db import models
from django.utils.translation import gettext_lazy as _

from ruchky_backend.helpers.db.models import UUIDMixin, DateTimeMixin, generate_filename
from ruchky_backend.helpers.storage import storage
from ruchky_backend.users.models import User


class Species(models.TextChoices):
    DOG = "dog", _("Dog")
    CAT = "cat", _("Cat")


class Sex(models.TextChoices):
    FEMALE = "f", _("Female")
    MALE = "m", _("Male")


class Pet(UUIDMixin, DateTimeMixin):
    """
    The core pet model: includes ownership by a User (which could be
    an individual or an organization/charity).
    """

    name = models.CharField(_("Name"), max_length=100)
    species = models.CharField(_("Species"), max_length=20, choices=Species.choices)
    breed = models.CharField(_("Breed"), max_length=100, blank=True, null=True)
    sex = models.CharField(_("Sex"), max_length=1, choices=Sex.choices)
    birth_date = models.DateField(_("Birth Date"))
    location = models.CharField(_("Location"), max_length=100, blank=True, null=True)
    is_vaccinated = models.BooleanField(_("Vaccinated"), default=False)

    description = models.TextField(_("Description"), blank=True, null=True)
    health = models.TextField(_("Health"), blank=True, null=True)
    profile_picture = models.ImageField(
        verbose_name=_("Profile Picture"),
        upload_to=generate_filename,
        storage=storage,
        blank=True,
        null=True,
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pets",
        verbose_name=_("Owner"),
    )

    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"


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
