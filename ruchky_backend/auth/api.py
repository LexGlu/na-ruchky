from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation, has_verified_email

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.middleware.csrf import get_token
from django.utils.translation import gettext as _
from ninja import Router

from ruchky_backend.auth.schemas import UserLogin, UserRegister
from ruchky_backend.helpers.api.schemas import BaseResponse

User = get_user_model()


router = Router(tags=["auth"])

# TODO: Add custom reset password, confirm reset password and change password endpoints (based on allauth)


@router.get("/csrf", response={200: BaseResponse})
def get_csrf_token(request):
    """
    Returns a CSRF token for the current session.
    """

    get_token(request)
    return {"message": "success"}


@router.post(
    "/login", response={200: BaseResponse, 401: BaseResponse, 403: BaseResponse}
)
def login_user(request, data: UserLogin):
    """
    Authenticates user using email + password.
    On success, sets Django session cookie (sessionid).
    Returns a JSON dict with status detail and HTTP 200.
    On failure, returns a 401 status with an error detail.
    """
    user = authenticate(request, email=data.email, password=data.password)
    if user is not None:
        if not has_verified_email(user):
            send_email_confirmation(request, user)
            return 403, {
                "message": _("We have sent you an email to verify your email address.")
            }

        login(request, user)
        return {"message": "Logged in"}
    return 401, {"message": _("Invalid сredentials. Please try again.")}


@router.post("/logout", response={200: BaseResponse})
def logout_user(request):
    logout(request)
    return {"message": "Logged out"}


@router.post("/register", response={200: BaseResponse, 400: BaseResponse})
def register_user(request, data: UserRegister):
    """
    Registers a new user. Sends an email confirmation link upon successfull registration.
    """
    try:
        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
        )
        send_email_confirmation(request, user)

    except IntegrityError:
        # Not to leak information about existing users we send the same message
        # But user will receive an email with information that account already exists
        adapter = get_adapter(request)
        adapter.send_account_already_exists_mail(data.email)
        return {"message": "success"}
    except Exception as e:
        return 500, {"message": str(e)}

    return {"message": "success"}
