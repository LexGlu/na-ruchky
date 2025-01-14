from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ruchky_backend.users.managers import UserManager
from ruchky_backend.helpers.db.models import UUIDMixin, DateTimeMixin, generate_filename
from ruchky_backend.helpers.db.validators import phone_validator
from ruchky_backend.helpers.storage import storage


class OrganizationProfile(UUIDMixin, DateTimeMixin):
    """
    Holds additional fields for organizational or charity users.
    Linked via OneToOneField to the main User model.
    """

    name = models.CharField(_("Organization Name"), max_length=255)
    address = models.CharField(_("Address"), max_length=255, blank=True, null=True)
    is_charity = models.BooleanField(_("Is Charity"), default=False)

    logo = models.ImageField(
        verbose_name=_("Organization Logo"),
        upload_to=generate_filename,
        storage=storage,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class User(AbstractUser, UUIDMixin):
    email = models.EmailField(_("Email address"), unique=True)
    username = None

    first_name = models.CharField(
        _("First name"), max_length=255, blank=True, null=True
    )
    last_name = models.CharField(_("Last name"), max_length=255, blank=True, null=True)
    phone = models.CharField(
        _("Phone number"),
        max_length=255,
        validators=[phone_validator],
        blank=True,
        null=True,
    )

    organization = models.ForeignKey(
        OrganizationProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="users",
        verbose_name=_("Organization"),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = " ".join(part for part in [self.first_name, self.last_name] if part)
        return full_name if full_name else None
