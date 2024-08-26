import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "google_meet_django.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import google_meet_django.users.signals  # noqa: F401
