from allauth.account.forms import (
    LoginForm as BaseLoginForm,
    ResetPasswordForm as BaseResetPasswordForm,
    ResetPasswordKeyForm as BaseResetPasswordKeyForm,
    SignupForm as BaseSignupForm,
)


class StripPlaceholdersMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():  # type: ignore[attr-defined]
            field.widget.attrs.pop("placeholder", None)


class LoginForm(StripPlaceholdersMixin, BaseLoginForm):
    pass


class SignupForm(StripPlaceholdersMixin, BaseSignupForm):
    pass


class ResetPasswordForm(StripPlaceholdersMixin, BaseResetPasswordForm):
    pass


class ResetPasswordKeyForm(StripPlaceholdersMixin, BaseResetPasswordKeyForm):
    pass
