
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import (
    CharField, DateTimeField, DurationField, EmailField, ForeignKey, JSONField, ManyToManyField, URLField)
from django.db.models import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Google-Meet-Django.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None
    last_name = None
    email = EmailField(_("email address"), unique=True)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class ServiceToken(models.Model):
    provider = CharField(_("Name of Serice Provider"), max_length=255)
    user = ForeignKey(User, related_name="serivce_token", on_delete=models.CASCADE)
    token = JSONField(_("Token"), default=dict)


class Session(models.Model):
    name = CharField(_("Name of Session"), max_length=255)
    attendee = ManyToManyField(User)
    start_time = DateTimeField(_("Start Time"))
    end_time = DateTimeField(_("End Time"))
    session_url = URLField(_("Session URL"), null=True, blank=True)
    session_time = DurationField(_("Session Duration"), null=True, blank=True)
