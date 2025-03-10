# Generated by Django 5.1.4 on 2025-01-14 11:27

import django.core.files.storage
import django.db.models.deletion
import ruchky_backend.helpers.db.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganizationProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created At"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated At"),
                ),
                (
                    "name",
                    models.CharField(max_length=255, verbose_name="Organization Name"),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Address"
                    ),
                ),
                (
                    "is_charity",
                    models.BooleanField(default=False, verbose_name="Is Charity"),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        null=True,
                        storage=django.core.files.storage.FileSystemStorage(),
                        upload_to=ruchky_backend.helpers.db.models.generate_filename,
                        verbose_name="Organization Logo",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="user",
            name="organization",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="users.organizationprofile",
                verbose_name="Organization",
            ),
        ),
    ]
