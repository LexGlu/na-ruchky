from allauth.account.adapter import get_adapter
from allauth.account.utils import send_email_confirmation, has_verified_email
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.models import SocialLogin

from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.middleware.csrf import get_token
from django.utils.translation import gettext as _
from ninja import Router
from ninja.responses import Response


from ruchky_backend.auth.schemas import UserLogin, UserRegister, TokenSchema
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


@router.post("/google-login")
def google_login(request, data: TokenSchema):
    """
    Authenticate a user using Google OAuth token
    """
    provider = "google"
    token = data.token
    try:
        adapter = GoogleOAuth2Adapter(request)
        app = SocialApp.objects.get(provider=provider)
        social_login: SocialLogin = adapter.complete_login(
            request, app, token=token, response={"id_token": token}
        )

        email = (
            social_login.email_addresses[0] if social_login.email_addresses else None
        )
        if not email:
            return Response({"message": "Email not provided by Google"}, status=400)

        if not social_login.is_existing:
            social_login.lookup()
            user_exists = User.objects.filter(email=email.email).exists()
            if user_exists:
                social_account_exists = social_login.user.socialaccount_set.filter(
                    provider=provider
                ).exists()

                if not social_account_exists:
                    print(f"User does not have {provider} account, connecting")
                    social_login.connect(request, user=social_login.user)
            else:
                print("Creating new user since user does not exists.")
                social_login.save(request)

        user = social_login.account.user

        if not user.is_active:
            return Response({"message": "Account is disabled"}, status=403)

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        return Response("")
    except SocialApp.DoesNotExist:
        return Response(
            {"message": "Google authentication is not configured"}, status=500
        )
    except Exception as e:
        print(f"Google login error: {str(e)}")
        return Response({"message": "Authentication failed"}, status=401)
