from ruchky_backend.users.forms import (
    LoginForm,
    SignupForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
)


def auth_forms(request):
    return {
        "login_form": LoginForm(),
        "signup_form": SignupForm(),
        "reset_password_form": ResetPasswordForm(),
        "reset_password_key_form": ResetPasswordKeyForm(),
    }
