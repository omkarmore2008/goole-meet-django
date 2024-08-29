from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from google_meet_django.users.models import ServiceToken, Session, User
from google_meet_django.utils.calendar_event import create_event


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = "__all__"


class SessionSerializer(serializers.ModelSerializer[Session]):
    class Meta:
        model = Session
        fields = "__all__"

    def create(self, validated_data):
        session_data = create_event(validated_data)
        if session_data:
            validated_data["session_id"] = session_data["id"]
            validated_data["session_data"] = session_data
            return super().create(validated_data)
        raise ValidationError({"error": "Failed to create event and retrieve session URL. Please confirm you've valid google meet consent"})


class ServiceTokenSerializer(serializers.ModelSerializer[ServiceToken]):
    class Meta:
        model = ServiceToken
        fields = "__all__"
