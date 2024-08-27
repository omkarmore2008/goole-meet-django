from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from google_meet_django.users.api.views import UsersAPIView, LoginLogoutView, ServiceTokensAPIView, SessionsAPIView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UsersAPIView, basename="users")
router.register("auth", LoginLogoutView, basename="auth")
router.register("service_token", ServiceTokensAPIView, basename="service_token")
router.register("session", SessionsAPIView, basename="session")


app_name = "api"
urlpatterns = router.urls
