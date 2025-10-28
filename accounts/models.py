from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("Email requerido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)
        extra.setdefault("is_approved", True)
        return self.create_user(email, password, **extra)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=50, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, default="pending")
    # password provisto por AbstractBaseUser
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_date = models.DateTimeField(null=True, blank=True)
    portal_used = models.CharField(max_length=100, blank=True)
    total_investment = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # admin approve for non-whitelisted domains
    business_domain = models.CharField(max_length=255, blank=True, null=True)
    twofa_enabled = models.BooleanField(default=False)
    twofa_secret = models.CharField(max_length=128, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.email

#managament white list
class DomainWhitelist(models.Model):
    domain = models.CharField(max_length=255, unique=True)
    auto_approve = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RegistrationRequest(models.Model):
    email = models.EmailField()
    domain = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[("pending","pending"),("approved","approved"),("denied","denied")], default="pending")
    admin_note = models.TextField(blank=True, null=True)
