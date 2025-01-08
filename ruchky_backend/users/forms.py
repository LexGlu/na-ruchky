from allauth.account.forms import (
    LoginForm as LoginFormBase,
    ResetPasswordForm as ResetPasswordFormBase,
    ResetPasswordKeyForm as ResetPasswordKeyFormBase,
    SignupForm as SignupFormBase,
)
from django.utils.translation import gettext_lazy as _


class LoginForm(LoginFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["login"].label = _("E-mail address")
        self.fields["login"].widget.attrs.update(
            {
                "placeholder": _("E-mail address"),
                "autofocus": "autofocus",
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
            }
        )

        self.fields["password"].label = _("Password")
        self.fields["password"].widget.attrs.update(
            {
                "placeholder": _("Password"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
            }
        )

        self.fields["remember"].label = _("Remember me")
        self.fields["remember"].widget.attrs.update(
            {
                "class": "form-check-input",
            }
        )
        self.fields["remember"].label_suffix = ""


class ResetPasswordForm(ResetPasswordFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = _("E-mail address")
        self.fields["email"].widget.attrs.update(
            {
                "autofocus": "autofocus",
                "placeholder": _("Enter your e-mail address"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
                "id": "reset_email_id",
            }
        )


class ResetPasswordKeyForm(ResetPasswordKeyFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = _("Password")
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": _("Enter your password"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
            }
        )
        self.fields["password2"].label = _("Confirm password")
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": _("Confirm your password"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
            }
        )


class SignupForm(SignupFormBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = _("E-mail address")
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": _("E-mail address"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
                "autofocus": "autofocus",
            }
        )

        self.fields["password1"].label = _("Password")
        self.fields["password1"].widget.attrs.update(
            {
                "placeholder": _("Enter your password"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
            }
        )

        # remove password help text
        self.fields["password1"].help_text = ""

        self.fields["password2"].label = _("Confirm password")
        self.fields["password2"].widget.attrs.update(
            {
                "placeholder": _("Confirm your password"),
                "class": "form-control auth-input py-075 px-3 body-regular-14 text-black",
            }
        )
