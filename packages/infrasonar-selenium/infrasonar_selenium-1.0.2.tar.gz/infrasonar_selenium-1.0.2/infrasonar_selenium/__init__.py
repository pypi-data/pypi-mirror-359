import os
from .base import TestBase  # noqa: F401


def get_password() -> str | None:
    return os.getenv('PASSWORD')


def get_secret() -> str | None:
    return os.getenv('SECRET')
