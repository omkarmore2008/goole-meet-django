from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from rest_framework import parsers, status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from google_meet_django.users.models import User
from google_meet_django.users.api.serializers import UserSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination


class LoginLogoutView(viewsets.ViewSet, TokenRefreshView):
    permission_classes = [AllowAny]

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

    def refresh_token(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                login_data = {
                    "token": {
                        "refresh": request.data["refresh"],
                        "access": response.data["access"],
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
                {"error": "Login failed"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

class UsersAPIView(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "post", "delete"]
    pagination_class = PageNumberPagination

    def get(self, request):
        return Response({
                "data": self.serializer_class(self.queryset, many=True).data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        data = request.data.copy()
        serialzier = self.serializer_class(data=data)
        if serialzier.is_valid():
            serialzier.save()
            return Response({"User Created Successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": serialzier.errors}, status=status.HTTP_400_BAD_REQUEST)