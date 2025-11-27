from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenRefreshView,
	TokenVerifyView,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	username_field = 'email'
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['email'] = self.fields.pop('username')
	
	def validate(self, attrs):
		email = attrs.get('email')
		password = attrs.get('password')
		
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			raise ValueError('No usuario encontrado')
		
		if not user.check_password(password):
			raise ValueError('Contraseña incorrecta')
		
		if not user.is_active:
			raise ValueError('Usuario desactivado')
		
		refresh = self.get_token(user)
		return {
			'refresh': str(refresh),
			'access': str(refresh.access_token),
			'user': {
				'id': user.id,
				'username': user.username,
				'email': user.email,
				'first_name': user.first_name,
				'last_name': user.last_name,
			}
		}


class CustomTokenObtainPairView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer
	permission_classes = [AllowAny]


urlpatterns = [
	path('admin/', admin.site.urls),
	
	path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	
	# ← NUEVO ENDPOINT
	path('api/v1/dashboard/auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
	
	path('api/v1/dashboard/', include('apps.pragma_dashboard.urls')),
]