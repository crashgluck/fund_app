from django.urls import path
from .views import RegisterView, MeView, Generate2FAView, Verify2FAView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("2fa/generate/", Generate2FAView.as_view(), name="2fa_generate"),
    path("2fa/verify/", Verify2FAView.as_view(), name="2fa_verify"),
]
