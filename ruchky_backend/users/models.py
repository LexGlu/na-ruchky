from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from ruchky_backend.users.managers import UserManager
from ruchky_backend.helpers.db.models import UUIDMixin
from ruchky_backend.helpers.db.validators import phone_validator


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

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        full_name = " ".join(part for part in [self.first_name, self.last_name] if part)
        return full_name if full_name else None
