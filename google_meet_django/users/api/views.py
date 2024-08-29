import base64
import json

from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from google_meet_django.users.models import User, ServiceToken, Session
from google_meet_django.users.api.serializers import UserSerializer, ServiceTokenSerializer, SessionSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

import google_auth_oauthlib.flow

from google_meet_django.utils.calendar_event import generate_redirect_uri


class LoginLogoutView(viewsets.ViewSet, TokenRefreshView):
    permission_classes = [AllowAny]

    @action(
        detail=False,
        methods=["post"],
        url_path="login",
    )
    def user_login(self, request):
        request_data = request.data.copy()
        email = request_data.get("email", "").lower()
        password = request_data.get("password", "")

        if not email or not password:
            return Response(
                {
                    "error": "Please provide required data.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {
                    "error": "Your authentication information is incorrect. Please try again.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh = RefreshToken.for_user(user) 
        login_data = {
            "token": {
                "refreshToken": str(refresh),
                "accessToken": str(refresh.access_token),
                "lifetime": refresh.lifetime
            },
            "message": "Logged in successfully",
            "last_login": user.last_login,
            "user": UserSerializer(user, context={'request': request}).data
        }
        return Response(login_data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
    )
    def user_logout(self, request):
        try:
            logout(request)
            return Response({"message": "User logged out successfullly!"}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", str(e))
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=["post"],
        url_path="refresh",
    )
    def refresh_token(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                login_data = {
                    "token": {
                        "refreshToken": request.data["refresh"],
                        "accessToken": response.data["access"],
                    },
                    "message": "Logged in successfully.",
                }
                return Response(login_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Login failed"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        except Exception as e:
            print("Error:", str(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class UsersAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "post", "delete"]
    pagination_class = PageNumberPagination

class ServiceTokensAPIView(viewsets.ModelViewSet):
    queryset = ServiceToken.objects.all()
    serializer_class = ServiceTokenSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "post", "delete"]
    pagination_class = PageNumberPagination


class SessionsAPIView(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "post", "delete"]
    pagination_class = PageNumberPagination

    def create(self, request):
        request_data = request.data.copy()
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CalendarServiceViewset(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, AllowAny]
    http_method_names = ["post", "get"]

    def get_permissions(self):
        if self.action == "get":
            return [permission() for permission in [AllowAny]]
        return [permission() for permission in self.permission_classes]

    @action(
        detail=False,
        methods=["post"],
        url_path="auth_url",
    )
    def post(self, request):
        redirect_uri = generate_redirect_uri(request=request)
        user_info = UserSerializer(request.user).data
        serialized_data = json.dumps(user_info).encode("utf-8")
        encoded_string = base64.b64encode(serialized_data).decode("utf-8")
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            settings.CREDS_JSON,
            scopes=settings.SCOPES,
            state=encoded_string,
            redirect_uri=redirect_uri
        )
        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            login_hint=request.user.email,
            prompt="consent",
        )
        return Response({"auth_url": authorization_url}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="callback",
    )
    def get(self, request):
        try:
            redirect_uri = generate_redirect_uri(request=request)
            auth_code = request.GET.get("code")
            state = request.query_params.get("state")
            decoded_bytes = base64.b64decode(state)
            user_info = json.loads(decoded_bytes.decode("utf-8"))
            flow = google_auth_oauthlib.flow.Flow.from_client_config(
                settings.CREDS_JSON, settings.SCOPES, redirect_uri=redirect_uri
            )
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            user = User.objects.get(id=user_info.get("id"))
            calendar_service_object, _ = ServiceToken.objects.get_or_create(
                user=user, provider=settings.SERVICE_PROVIDER
            )
            calendar_service_object.token = json.loads(credentials.to_json())
            calendar_service_object.save()
            return Response(
                {"message": "Token generated successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
