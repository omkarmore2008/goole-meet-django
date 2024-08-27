from collections.abc import Sequence
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from google_meet_django.users.models import User, ServiceToken, Session
from google_meet_django.users.api.serializers import UserSerializer, ServiceTokenSerializer, SessionSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action


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
                    "error": "Your authentication information is incorrect. Please try again.",
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
        token = {
            "refreshToken": str(refresh),
            "accessToken": str(refresh.access_token),
            "lifetime": refresh.lifetime
        }
        login_data = {
            "token": token,
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


class SessionsAPIView(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "post", "delete"]
    pagination_class = PageNumberPagination

    def create(self, request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)