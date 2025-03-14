# Generated by Django 5.1.6 on 2025-03-14 14:34

import django.core.files.storage
import django.db.models.deletion
import ruchky_backend.helpers.db.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pets", "0004_petimage_alter_pet_profile_picture"),
    ]

    operations = [
        migrations.CreateModel(
            name="Breed",
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
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                (
                    "species",
                    models.CharField(
                        choices=[("dog", "Dog"), ("cat", "Cat")],
                        max_length=20,
                        verbose_name="Species",
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Description"),
                ),
                (
                    "life_span",
                    models.CharField(
                        blank=True,
                        help_text="Average life span of the breed",
                        max_length=50,
                        null=True,
                        verbose_name="Life Span",
                    ),
                ),
                (
                    "weight",
                    models.CharField(
                        blank=True,
                        help_text="Average weight of the breed",
                        max_length=50,
                        null=True,
                        verbose_name="Weight",
                    ),
                ),
                (
                    "origin",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Origin"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Representative image of the breed",
                        null=True,
                        storage=django.core.files.storage.FileSystemStorage(),
                        upload_to=ruchky_backend.helpers.db.models.generate_filename,
                        verbose_name="Breed Image",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
            ],
            options={
                "verbose_name": "Breed",
                "verbose_name_plural": "Breeds",
                "ordering": ["species", "name"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("name", "species"), name="unique_breed_per_species"
                    )
                ],
            },
        ),
        migrations.AlterField(
            model_name="pet",
            name="breed",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pets",
                to="pets.breed",
                verbose_name="Breed",
            ),
        ),
    ]
