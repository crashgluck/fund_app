from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
import pyotp
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

# 2FA endpoints
class Generate2FAView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user
        if user.twofa_secret is None:
            secret = pyotp.random_base32()
            user.twofa_secret = secret
            user.save()
        else:
            secret = user.twofa_secret
        # otpauth URL for QR
        otpauth = pyotp.totp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="TreasuryPlatform")
        return Response({"otpauth_url": otpauth})

class Verify2FAView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        token = request.data.get("token")
        user = request.user
        if not user.twofa_secret:
            return Response({"detail":"2FA not initialized"}, status=400)
        totp = pyotp.TOTP(user.twofa_secret)
        if totp.verify(token, valid_window=1):
            user.twofa_enabled = True
            user.save()
            return Response({"detail":"2FA enabled"})
        return Response({"detail":"Invalid token"}, status=400)


# 🔹 Logout (invalida el refresh token)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # Necesita tener habilitado Blacklist en settings.py
            return Response({"detail": "Sesión cerrada correctamente"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email requerido"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

            send_mail(
                "Recuperar contraseña",
                f"Para restablecer tu contraseña, haz clic en: {reset_link}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

            return Response({"detail": "Se ha enviado un correo con el enlace para restablecer tu contraseña."})

        except User.DoesNotExist:
            return Response({"detail": "No existe un usuario con ese correo."}, status=status.HTTP_404_NOT_FOUND)

# 🔹 Confirmar el cambio de contraseña
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        if not uid or not token or not new_password:
            return Response({"detail": "Datos incompletos."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Enlace inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Contraseña restablecida correctamente."})
        else:
            return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)