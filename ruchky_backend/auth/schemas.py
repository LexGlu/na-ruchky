from typing import Optional

from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from ninja import Schema
from pydantic import EmailStr, field_validator

from ruchky_backend.helpers.types import PhoneNumber


class UserLogin(Schema):
    email: EmailStr
    password: str


class UserRegister(Schema):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[PhoneNumber] = None

    @field_validator("password")
    def validate_pass(cls, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise ValueError("; ".join(e.messages))
        return value


class TokenSchema(Schema):
    token: str
