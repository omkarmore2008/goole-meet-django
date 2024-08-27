from rest_framework import serializers

from google_meet_django.users.models import ServiceToken, Session, User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = "__all__"


class SessionSerializer(serializers.ModelSerializer[Session]):
    class Meta:
        model = Session
        fields = "__all__"


class ServiceTokenSerializer(serializers.ModelSerializer[ServiceToken]):
    class Meta:
        model = ServiceToken
        fields = "__all__"
