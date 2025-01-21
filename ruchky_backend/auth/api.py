from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.middleware.csrf import get_token
from ninja import Router

from ruchky_backend.auth.schemas import UserLogin, UserRegister
from ruchky_backend.users.schemas import UserSchema
from ruchky_backend.helpers.api.schemas import BaseResponse

User = get_user_model()


router = Router(tags=["auth"])


@router.get("/csrf", response={200: BaseResponse})
def get_csrf_token(request):
    """
    Returns a CSRF token for the current session.
    """

    get_token(request)
    return {"message": "CSRF token set"}


@router.post("/login", response={200: BaseResponse, 401: BaseResponse})
def login_user(request, data: UserLogin):
    """
    Authenticates user using email + password.
    On success, sets Django session cookie (sessionid).
    Returns a JSON dict with status detail and HTTP 200.
    On failure, returns a 401 status with an error detail.
    """
    user = authenticate(request, email=data.email, password=data.password)
    if user is not None:
        login(request, user)
        return {"message": "Logged in"}
    return 401, {"message": "Invalid credentials"}


@router.post("/logout", response={200: BaseResponse})
def logout_user(request):
    logout(request)
    return {"message": "Logged out"}


@router.post("/register", response={200: UserSchema, 400: BaseResponse})
def register_user(request, data: UserRegister):
    """
    Registers a new user.
    Returns the created user (serialized via UserSchema).
    """
    try:
        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
        )
    except IntegrityError:
        return 400, {"message": "User with that email already exists."}
    except Exception as e:
        return 500, {"message": str(e)}

    return user
