from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenBlacklistView, TokenVerifyView
)
from rest_framework import routers

from drf_spectacular.utils import extend_schema, extend_schema_view

from users.views import (
    UserCreateView,
    UserRetrieveUpdateView, UserViewSet
)


app_name="users"

router = routers.DefaultRouter()
router.register("users", UserViewSet)



@extend_schema_view(post=extend_schema(tags=["auth"]))
class LoginView(TokenObtainPairView):
    pass


@extend_schema_view(post=extend_schema(tags=["auth"]))
class RefreshTokenView(TokenRefreshView):
    pass


@extend_schema_view(post=extend_schema(tags=["auth"]))
class VerifyTokenView(TokenVerifyView):
    pass


@extend_schema_view(post=extend_schema(tags=["auth"]))
class LogoutView(TokenBlacklistView):
    pass


urlpatterns = [
    path("register/", UserCreateView.as_view(), name="register"),
    path("token/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("token/verify/", VerifyTokenView.as_view(), name="token_verify"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("users/me/", UserRetrieveUpdateView.as_view(), name="retrieve-profile"),
    path("", include(router.urls)),
]

