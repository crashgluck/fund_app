from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterView,
    MeView,
    Generate2FAView,
    Verify2FAView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    # Registro y autenticación
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),  # ✅ NUEVO logout JWT
    path("me/", MeView.as_view(), name="me"),

    # 2FA
    path("2fa/generate/", Generate2FAView.as_view(), name="2fa_generate"),
    path("2fa/verify/", Verify2FAView.as_view(), name="2fa_verify"),

    # Recuperar contraseña
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]
