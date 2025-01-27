from ninja import ModelSchema

from ruchky_backend.users.models import User


class UserSchema(ModelSchema):
    class Meta:
        model = User
        fields = "id", "email", "first_name", "last_name", "phone"
