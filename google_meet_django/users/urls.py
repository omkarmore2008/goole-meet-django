from django.urls import path

from .views import UsersAPIView, LoginLogoutView

app_name = "users"
urlpatterns = [
    path("users", view=UsersAPIView.as_view({
        "get": "get",
        "post": "post",
        # "put": "put",
        # "delete": "delete"
    }), name="users"),
    path(
        "login",
        LoginLogoutView.as_view({"post": "user_login"}),
        name="login"
    ),
    path(
        "logout",
        LoginLogoutView.as_view({"post": "user_logout"}),
        name="logout",
    ),
    path(
        "refresh",
        LoginLogoutView.as_view({"post": "refresh_token"}),
        name="refresh_token",
    ),
]
