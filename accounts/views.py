from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer
from .models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
import pyotp
from rest_framework.views import APIView

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
