import os
import re
from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def slugify_camelcase(string: str, sep: str = "-") -> str:
    """
    Converts camelcase string to lowercase string divided with given
    separator

    :param string: string to slugify
    :param sep: separator
    :return: slugified string

    With sep='_':
        'CamelCase' -> 'camel_case'
    """
    repl = r"\1{}\2".format(sep)
    s1 = re.sub("(.)([A-Z][a-z]+)", repl, string)
    return re.sub("([a-z0-9])([A-Z])", repl, s1).lower()


def generate_filename(instance: models.Model, filename: str) -> str:
    """
    Generates a filename for a model's instance

    :param instance: Django model's instance
    :param filename: filename
    :return: generated filename

    Filename consist of slugified model name, current datetime and time
    and uuid
    """
    f, ext = os.path.splitext(filename)
    model_name = slugify_camelcase(instance._meta.model.__name__, "_")
    strftime = timezone.datetime.now()
    hex_ = uuid4().hex
    return f"{model_name}/{hex_}_{strftime}{ext}"


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class DateTimeMixin(models.Model):
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        abstract = True
