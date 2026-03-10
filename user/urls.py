from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    RegisterView,
    SessionLoginView,
    LogoutView,
    MeView,
)

urlpatterns = [

    # registration
    path("register/", RegisterView.as_view(), name="register"),

    # session authentication
    path("session/login/", SessionLoginView.as_view(), name="session_login"),
    path("session/logout/", LogoutView.as_view(), name="session_logout"),

    # jwt authentication (standard simplejwt views)
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # current user
    path("me/", MeView.as_view(), name="me"),
]

app_name = "user"
