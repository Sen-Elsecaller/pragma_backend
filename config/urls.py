from django.contrib import admin
from django.urls import path, include
from apps.pragma_dashboard.views import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path("admin/", admin.site.urls),

    # LOGIN POR EMAIL
    path("api/v1/dashboard/auth/login/", CustomTokenObtainPairView.as_view(), name="auth_login"),

    # SimpleJWT
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Resto del dashboard
    path("api/v1/dashboard/", include("apps.pragma_dashboard.urls")),
]
