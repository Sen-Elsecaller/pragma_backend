from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView


# ============================================
# AUTENTICACIÓN CUSTOMIZADA - LOGIN CON EMAIL
# ============================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer que acepta email en lugar de username"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Reemplazar 'username' por 'email'
        if "username" in self.fields:
            self.fields["email"] = self.fields.pop("username")
            self.fields["email"].field_name = "email"

    def validate(self, attrs):
        """Validar credenciales usando email"""
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError({"detail": "Email y password son requeridos"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "No existe un usuario con este email"})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Contraseña incorrecta"})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "El usuario está desactivado"})

        # generar tokens
        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }


class CustomTokenObtainPairView(TokenObtainPairView):
    """Vista customizada para obtener tokens usando email"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


# ============================================
# URLS
# ============================================

urlpatterns = [
    path("admin/", admin.site.urls),

    # SOLO tu endpoint customizado de login por email
    path("api/v1/dashboard/auth/login/", CustomTokenObtainPairView.as_view(), name="auth_login"),

    # SimpleJWT tokens base
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Dashboard
    path("api/v1/dashboard/", include("apps.pragma_dashboard.urls")),
]
