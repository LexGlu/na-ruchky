from django.apps import AppConfig


class CustomAuthConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ruchky_backend.auth"
    label = "ruchky_auth"
