from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# Phone number format - https://en.wikipedia.org/wiki/E.164
phone_validator = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message=_(
        "Phone number must be entered in the format: '+999999999'. "
        "Up to 15 digits allowed."
    ),
)
