from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator


USERNAME_REGEX = r"[A-Za-z0-9._\-]{3,20}"


username_validators = [
    RegexValidator(
        regex=rf"^{USERNAME_REGEX}$",
        message="Username can only contain letters, numbers, dots, dashes and underscores.",
    ),
    MinLengthValidator(3, "Username must be at least 3 characters long."),
    MaxLengthValidator(20, "Username must be at most 20 characters long."),
]
