from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.shortcuts import Http404
from django.utils.timezone import localtime
from ninja import Router
from ninja_apikey.models import APIKey
from ninja_apikey.security import APIKeyAuth, generate_key

from apps.user.models import User
from apps.user.schema import (
    Message,
    UserIn,
    UserOut,
    UserSignIn,
    UserSignUpOut,
    UserUpdateIn,
    UserUpdateOut,
)

auth = APIKeyAuth()
router = Router()


@router.post("/", auth=None, response={200: UserSignUpOut, 409: Message})
def signup(request, userInfo: UserIn):

    if User.objects.filter(email=userInfo.email).exists():
        return 409, Message(message="message: Email address is already registered.")
    try:
        user = User.objects.create(username=userInfo.username, email=userInfo.email)
    except IntegrityError:
        return 409, Message(message="message: username is already registered.")
    user.set_password(userInfo.password)
    user.save()
    return UserSignUpOut.from_orm(user)


@router.post("/login", auth=None, response={200: UserOut, 401: Message})
def login(request, userInfo: UserSignIn):

    user = authenticate(request, username=userInfo.username, password=userInfo.password)
    if user is None:
        return 401, Message(message="Unauthorized")
    key = generate_key()
    APIKey.objects.create(
        prefix=key.prefix, hashed_key=key.hashed_key, user=user, label="login"
    )
    token = f"{key.prefix}.{key.key}"
    user.last_login = localtime().date()
    user.save()
    return UserOut(
        id=user.id,
        token=token,
        username=user.username,
        email=user.email,
    )


@router.post("/logout", response={200: Message, 401: Message})
def logout(request):
    if request.user.is_anonymous:
        return 401, Message(message="unauthorized")
    user_token = request.headers.get("X-API-Key")
    if not user_token:
        return 401, Message(message="No API key provided")
    data = user_token.split(".")
    if len(data) < 2:
        return 401, Message(message="Invalid API key format")
    prefix = data[0]
    user_APIkey = APIKey.objects.filter(prefix=prefix).first()
    user_APIkey.delete()
    return 200, Message(message="successful")


@router.patch("/", response={200: UserUpdateOut, 409: Message})
def user_update(request, newInfo: UserUpdateIn):
    try:
        user = User.objects.get(id=request.user.id)
    except User.DoesNotExist:
        raise Http404("User not found")

    if newInfo.email is not None:
        user.email = newInfo.email
    if newInfo.first_name is not None:
        user.first_name = newInfo.first_name
    if newInfo.last_name is not None:
        user.last_name = newInfo.last_name
    if newInfo.username is not None:
        user.username = newInfo.username
    if newInfo.password is not None:
        user.set_password(newInfo.password)
    try:
        user.save()
    except IntegrityError:
        return 409, Message(message="Username or email already exists.")
    return UserUpdateOut.from_orm(user)
