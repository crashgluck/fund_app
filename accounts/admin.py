from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, DomainWhitelist, RegistrationRequest

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "name", "is_staff", "is_active", "is_approved")
    list_filter = ("is_staff", "is_active", "is_approved")
    search_fields = ("email", "name")
    ordering = ("email",)

    # read only
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("name", "company", "title", "mobile", "business_type", "business_domain")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "is_approved", "groups", "user_permissions")}),
        ("2FA", {"fields": ("twofa_enabled", "twofa_secret")}),
        ("Fechas", {"fields": ("created_at", "updated_at", "terms_accepted", "terms_accepted_date")}),
        ("Datos del negocio", {"fields": ("portal_used", "total_investment", "status",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_active", "is_staff", "is_approved")}
        ),
    )

admin.site.register(User, UserAdmin)
admin.site.register(DomainWhitelist)