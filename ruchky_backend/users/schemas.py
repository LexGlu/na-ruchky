from ninja import ModelSchema

from ruchky_backend.users.models import User


class UserSchema(ModelSchema):
    class Meta:
        model = User
        exclude = [
            "password",
            "last_login",
            "user_permissions",
            "is_staff",
            "is_superuser",
            "groups",
            "is_active",
            "date_joined",
            "organization",
        ]
