from rest_framework import serializers

from google_meet_django.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = "__all__"

