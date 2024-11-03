from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from ninja import ModelSchema, Schema
from pydantic import ValidationInfo, field_validator

from apps.user.models import User


class UserIn(Schema):
    username: str
    email: str
    password: str

    @field_validator("password", mode="after")
    @classmethod
    def password_validator(
        cls, password: str, info: ValidationInfo, check_fields=False
    ):
        if password is None:
            raise ValueError("Password is required")
        if password == "":
            raise ValueError("password is requierd")
        if len(password) < 8:
            raise ValueError("password should be more than 8 charecters")
        return password

    @field_validator("email", mode="after", check_fields=False)
    @classmethod
    def email_validator(cls, email: str, info: ValidationInfo):
        if not email:
            raise ValueError

        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Enter a valid email address.")
        return email


class UserSignIn(Schema):
    username: str
    password: str


class Message(Schema):
    message: str


class UserUpdateIn(ModelSchema, UserIn):
    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name"]
        fields_optional = "__all__"


class UserUpdateOut(ModelSchema):
    class Meta:
        model = User
        fields = ["email", "username", "password", "first_name", "last_name"]
        fields_optional = "__all__"


class UserOut(Schema):
    id: int
    token: str
    username: str
    email: str


class UserSignUpOut(Schema):
    id: int
    username: str
    email: str
