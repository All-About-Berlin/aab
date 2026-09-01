from django.core.validators import RegexValidator


username_validators = [
    RegexValidator(
        regex=r"^[A-Za-z0-9.\-]+$",
        message="Username can only contain letters, numbers, dots and dashes.",
    ),
]
