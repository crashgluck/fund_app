from rest_framework import serializers
from .models import User, DomainWhitelist, RegistrationRequest
import tldextract
import pyotp
from .tasks import send_admin_email

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(required=False, allow_blank=True)
    company = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        ext = tldextract.extract(value)
        domain = f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain
        self.context['domain'] = domain
        return value

    def create(self, validated):
        domain = self.context.get('domain')
        if DomainWhitelist.objects.filter(domain=domain, auto_approve=True).exists():
            user = User.objects.create_user(email=validated["email"], password=validated["password"], name=validated.get("name",""), company=validated.get("company",""), business_domain=domain, is_active=True, is_approved=True)
            # send admin notification (task) -> your mail flow      

            subject = "Nuevo registro aprobado dentro de whitelist"
            message = f"Se registró un usuario con email {validated['email']} y dominio {domain}."
            admin_email = ["cris.vera.olivares@gmail.com"]

            # Enviar email en background
            send_admin_email.delay(subject, message, admin_email)
            return user
        else:
            # create user but inactive and registration request
            user = User.objects.create_user(email=validated["email"], password=validated["password"], name=validated.get("name",""), company=validated.get("company",""), business_domain=domain, is_active=False, is_approved=False)
            RegistrationRequest.objects.create(email=validated["email"], domain=domain)
            # send admin notification (task) -> your mail flow
           

            subject = "Nuevo registro pendiente de aprobación"
            message = f"Se registró un usuario con email {validated['email']} y dominio {domain}."
            admin_email = ["cris.vera.olivares@gmail.com"]

            # Enviar email en background
            send_admin_email.delay(subject, message, admin_email)

            return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","email","name","company","is_active","is_approved","twofa_enabled","business_domain")
