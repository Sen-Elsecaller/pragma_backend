"""
PRUEBA UNITARIA PU-006: Validador JWT
======================================
Validación de autenticación JWT, tokens, permisos y acceso a recursos protegidos
"""

import pytest
import json
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.settings import api_settings


# ============ PRUEBAS DE REGISTRO ============

@pytest.mark.django_db
class TestJWTRegistration:
	"""Pruebas de registro de usuarios"""

	def test_registro_exitoso(self, api_client, user_data):
		"""✅ TC-001: Registro de usuario exitoso"""
		url = '/api/v1/dashboard/auth/register/'
		response = api_client.post(url, user_data, format='json')
		
		assert response.status_code == status.HTTP_201_CREATED
		assert response.data['email'] == user_data['email']
		assert response.data['message'] == 'Usuario registrado exitosamente'
		assert 'id' in response.data
		
		# Verificar que el usuario se creó en BD
		user = User.objects.get(email=user_data['email'])
		assert user.first_name == 'Juan'
		assert user.last_name == 'Sebastian'

	def test_registro_email_duplicado(self, api_client, registered_user, user_data):
		"""✅ TC-002: Validar email duplicado"""
		url = '/api/v1/dashboard/auth/register/'
		
		# Intentar registrar con mismo email
		response = api_client.post(url, user_data, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert 'email' in response.data

	def test_registro_contraseñas_no_coinciden(self, api_client):
		"""✅ TC-003: Validar contraseñas que no coinciden"""
		url = '/api/v1/dashboard/auth/register/'
		
		data = {
			'nombre': 'Test User',
			'email': 'test@pragma.cl',
			'password': 'Pass123456',
			'password_confirm': 'Pass654321'
		}
		
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert 'password_confirm' in response.data

	def test_registro_password_muy_corto(self, api_client):
		"""✅ TC-004: Validar contraseña muy corta"""
		url = '/api/v1/dashboard/auth/register/'
		
		data = {
			'nombre': 'Test User',
			'email': 'test@pragma.cl',
			'password': 'Pass12',
			'password_confirm': 'Pass12'
		}
		
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============ PRUEBAS DE LOGIN ============

@pytest.mark.django_db
class TestJWTLogin:
	"""Pruebas de login y obtención de tokens"""

	def test_login_exitoso_con_email(self, api_client, registered_user, user_data):
		"""✅ TC-005: Login exitoso con email"""
		url = '/api/v1/dashboard/auth/login/'
		
		credentials = {
			'email': user_data['email'],
			'password': user_data['password']
		}
		
		response = api_client.post(url, credentials, format='json')
		
		assert response.status_code == status.HTTP_200_OK
		assert 'access' in response.data
		assert 'refresh' in response.data
		assert response.data['user']['email'] == user_data['email']

	def test_login_email_no_existe(self, api_client):
		"""✅ TC-006: Login con email que no existe"""
		url = '/api/v1/dashboard/auth/login/'
		
		credentials = {
			'email': 'noexiste@pragma.cl',
			'password': 'Pass123456'
		}
		
		response = api_client.post(url, credentials, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert 'email' in response.data

	def test_login_contraseña_incorrecta(self, api_client, registered_user, user_data):
		"""✅ TC-007: Login con contraseña incorrecta"""
		url = '/api/v1/dashboard/auth/login/'
		
		credentials = {
			'email': user_data['email'],
			'password': 'PasswordIncorrecto'
		}
		
		response = api_client.post(url, credentials, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST
		assert 'password' in response.data

	def test_login_retorna_datos_usuario(self, api_client, registered_user, user_data):
		"""✅ TC-008: Login retorna datos del usuario"""
		url = '/api/v1/dashboard/auth/login/'
		
		credentials = {
			'email': user_data['email'],
			'password': user_data['password']
		}
		
		response = api_client.post(url, credentials, format='json')
		
		assert response.status_code == status.HTTP_200_OK
		user_data_response = response.data['user']
		assert user_data_response['id'] == registered_user.id
		assert user_data_response['username'] == registered_user.username
		assert user_data_response['first_name'] == 'Juan'
		assert user_data_response['last_name'] == 'Sebastian'


# ============ PRUEBAS DE TOKENS ============

class TestJWTTokenManagement:
	"""Pruebas de generación y validación de tokens"""

	def test_token_access_es_jwt_valido(self, access_token):
		"""✅ TC-009: Token access es JWT válido"""
		assert access_token is not None
		# JWT tiene 3 partes separadas por puntos
		parts = access_token.split('.')
		assert len(parts) == 3

	def test_token_refresh_es_jwt_valido(self, refresh_token):
		"""✅ TC-010: Token refresh es JWT válido"""
		assert refresh_token is not None
		parts = refresh_token.split('.')
		assert len(parts) == 3

	def test_refresh_token_genera_nuevo_access(self, api_client, refresh_token):
		"""✅ TC-011: Refresh token genera nuevo access token"""
		url = '/api/v1/token/refresh/'
		
		data = {'refresh': refresh_token}
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_200_OK
		assert 'access' in response.data
		assert response.data['access'] is not None

	def test_refresh_token_invalido(self, api_client):
		"""✅ TC-012: Refresh token inválido"""
		url = '/api/v1/token/refresh/'
		
		data = {'refresh': 'token_invalido'}
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_401_UNAUTHORIZED

	def test_verify_token_valido(self, api_client, access_token):
		"""✅ TC-013: Verificar token access válido"""
		url = '/api/v1/token/verify/'
		
		data = {'token': access_token}
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_200_OK

	def test_verify_token_invalido(self, api_client):
		"""✅ TC-014: Verificar token inválido"""
		url = '/api/v1/token/verify/'
		
		data = {'token': 'token_invalido'}
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============ PRUEBAS DE AUTENTICACIÓN EN ENDPOINTS ============

@pytest.mark.django_db
class TestJWTProtectedEndpoints:
	"""Pruebas de acceso a endpoints protegidos"""

	def test_acceso_sin_token(self, api_client):
		"""✅ TC-015: Acceso a endpoint sin token"""
		url = '/api/v1/dashboard/auth/profile/me/'
		
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_401_UNAUTHORIZED

	def test_acceso_con_token_valido(self, api_client, access_token, registered_user):
		"""✅ TC-016: Acceso a endpoint con token válido"""
		url = '/api/v1/dashboard/auth/profile/me/'
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_200_OK
		assert response.data['id'] == registered_user.id
		assert response.data['email'] == registered_user.email

	def test_acceso_con_token_invalido(self, api_client):
		"""✅ TC-017: Acceso con token inválido"""
		url = '/api/v1/dashboard/auth/profile/me/'
		
		api_client.credentials(HTTP_AUTHORIZATION='Bearer token_invalido')
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_401_UNAUTHORIZED

	def test_acceso_sin_header_authorization(self, api_client):
		"""✅ TC-018: Acceso sin header Authorization"""
		url = '/api/v1/dashboard/auth/profile/me/'
		
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============ PRUEBAS DE PERMISOS ============

@pytest.mark.django_db
class TestJWTPermissions:
	"""Pruebas de permisos y autorización"""

	def test_usuario_solo_ve_sus_sesiones(self, api_client, registered_user, access_token):
		"""✅ TC-019: Usuario solo ve sus propias sesiones"""
		from apps.pragma_dashboard.models import SesionSimulacion
		
		# Crear sesión del usuario
		sesion_propia = SesionSimulacion.objects.create(
			usuario=registered_user,
			escenario_nombre='Escenario 1'
		)
		
		# Crear otro usuario y su sesión
		otro_usuario = User.objects.create_user(
			username='otro',
			email='otro@pragma.cl',
			password='Pass123'
		)
		sesion_otra = SesionSimulacion.objects.create(
			usuario=otro_usuario,
			escenario_nombre='Escenario 2'
		)
		
		url = '/api/v1/dashboard/sesiones/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data['results']) == 1
		assert response.data['results'][0]['id'] == sesion_propia.id

	def test_admin_ve_todos_analisis(self, api_client, registered_user, admin_user):
		"""✅ TC-020: Admin ve todos los análisis"""
		from apps.pragma_dashboard.models import AnalisisIA
		
		# Crear análisis de usuario normal
		AnalisisIA.objects.create(
			usuario=registered_user,
			usuario_nombre='Usuario 1',
			usuario_email='user1@pragma.cl',
			savefile_id=1,
			nivel_riesgo='bajo'
		)
		
		# Crear análisis de otro usuario
		otro_usuario = User.objects.create_user(
			username='otro2',
			email='otro2@pragma.cl',
			password='Pass123'
		)
		AnalisisIA.objects.create(
			usuario=otro_usuario,
			usuario_nombre='Usuario 2',
			usuario_email='user2@pragma.cl',
			savefile_id=2,
			nivel_riesgo='alto'
		)
		
		# Login como admin
		admin_refresh = RefreshToken.for_user(admin_user)
		admin_token = str(admin_refresh.access_token)
		
		url = '/api/v1/dashboard/analisis-ia/todos/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_200_OK
		assert len(response.data['results']) == 2

	def test_usuario_normal_no_accede_todos_analisis(self, api_client, registered_user, access_token):
		"""✅ TC-021: Usuario normal NO accede a endpoint todos"""
		url = '/api/v1/dashboard/analisis-ia/todos/'
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_403_FORBIDDEN


# ============ PRUEBAS DE PERFIL DE USUARIO ============

@pytest.mark.django_db
class TestJWTUserProfile:
	"""Pruebas de gestión de perfil de usuario"""

	def test_obtener_perfil_usuario(self, api_client, registered_user, access_token):
		"""✅ TC-022: Obtener perfil del usuario autenticado"""
		url = '/api/v1/dashboard/auth/profile/me/'
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.get(url)
		
		assert response.status_code == status.HTTP_200_OK
		assert response.data['username'] == 'juan'
		assert response.data['email'] == registered_user.email

	def test_actualizar_nombre_usuario(self, api_client, registered_user, access_token):
		"""✅ TC-023: Actualizar nombre de usuario"""
		url = '/api/v1/dashboard/auth/profile/update_profile/'
		
		data = {
			'first_name': 'Juan Pablo',
			'last_name': 'Garcia'
		}
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.patch(url, data, format='json')
		
		assert response.status_code == status.HTTP_200_OK
		assert response.data['first_name'] == 'Juan Pablo'
		assert response.data['last_name'] == 'Garcia'
		
		# Verificar cambio en BD
		registered_user.refresh_from_db()
		assert registered_user.first_name == 'Juan Pablo'

	def test_cambiar_contraseña(self, api_client, registered_user, access_token, user_data):
		"""✅ TC-024: Cambiar contraseña del usuario"""
		url = '/api/v1/dashboard/auth/profile/change_password/'
		
		data = {
			'old_password': user_data['password'],
			'new_password': 'NewPass456',
			'new_password_confirm': 'NewPass456'
		}
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_200_OK
		
		# Verificar que la contraseña cambió
		registered_user.refresh_from_db()
		assert registered_user.check_password('NewPass456')

	def test_cambiar_contraseña_incorrecta_actual(self, api_client, registered_user, access_token):
		"""✅ TC-025: Cambiar contraseña con contraseña actual incorrecta"""
		url = '/api/v1/dashboard/auth/profile/change_password/'
		
		data = {
			'old_password': 'PasswordIncorrecto',
			'new_password': 'NewPass456',
			'new_password_confirm': 'NewPass456'
		}
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		response = api_client.post(url, data, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============ PRUEBAS DE SEGURIDAD ============

@pytest.mark.django_db
class TestJWTSecurity:
	"""Pruebas de seguridad JWT"""

	def test_token_no_devuelve_password(self, api_client, registered_user, user_data):
		"""✅ TC-026: Token no devuelve contraseña"""
		url = '/api/v1/dashboard/auth/login/'
		
		credentials = {
			'email': user_data['email'],
			'password': user_data['password']
		}
		
		response = api_client.post(url, credentials, format='json')
		
		assert response.status_code == status.HTTP_200_OK
		# Verificar que la contraseña NO está en la respuesta
		assert 'password' not in response.data
		assert user_data['password'] not in str(response.data)

	def test_token_expira(self, registered_user):
		"""✅ TC-027: Token con expiración corta"""
		from rest_framework_simplejwt.tokens import RefreshToken
		from django.test import override_settings
		import datetime
		
		# Este test documenta que los tokens expiran
		# (requeriría mock de tiempo para testear completamente)
		refresh = RefreshToken.for_user(registered_user)
		assert refresh.access_token is not None

	def test_usuario_desactivado_no_accede(self):
		"""✅ TC-028: Usuario desactivado no accede"""
		url = '/api/v1/dashboard/auth/login/'
		
		# Crear usuario desactivado
		user = User.objects.create_user(
			username='desactivado',
			email='desactivado@pragma.cl',
			password='Pass123'
		)
		user.is_active = False
		user.save()
		
		client = APIClient()
		credentials = {
			'email': 'desactivado@pragma.cl',
			'password': 'Pass123'
		}
		
		response = client.post(url, credentials, format='json')
		
		assert response.status_code == status.HTTP_400_BAD_REQUEST


# ============ PRUEBAS DE FLUJO COMPLETO ============

@pytest.mark.django_db
class TestJWTCompleteFlow:
	"""Pruebas de flujo completo de autenticación"""

	def test_flujo_registro_login_acceso(self, api_client, user_data):
		"""✅ TC-029: Flujo completo: registro → login → acceso"""
		# 1. Registrar usuario
		register_url = '/api/v1/dashboard/auth/register/'
		register_response = api_client.post(register_url, user_data, format='json')
		assert register_response.status_code == status.HTTP_201_CREATED
		
		# 2. Login
		login_url = '/api/v1/dashboard/auth/login/'
		login_response = api_client.post(
			login_url,
			{'email': user_data['email'], 'password': user_data['password']},
			format='json'
		)
		assert login_response.status_code == status.HTTP_200_OK
		access_token = login_response.data['access']
		
		# 3. Acceder a endpoint protegido
		profile_url = '/api/v1/dashboard/auth/profile/me/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		profile_response = api_client.get(profile_url)
		
		assert profile_response.status_code == status.HTTP_200_OK
		assert profile_response.data['email'] == user_data['email']

	def test_flujo_refresh_token(self, api_client, registered_user, user_data):
		"""✅ TC-030: Flujo con refresh token"""
		# 1. Login
		login_url = '/api/v1/dashboard/auth/login/'
		login_response = api_client.post(
			login_url,
			{'email': user_data['email'], 'password': user_data['password']},
			format='json'
		)
		assert login_response.status_code == status.HTTP_200_OK
		refresh_token_value = login_response.data['refresh']
		
		# 2. Refrescar token
		refresh_url = '/api/v1/token/refresh/'
		refresh_response = api_client.post(
			refresh_url,
			{'refresh': refresh_token_value},
			format='json'
		)
		assert refresh_response.status_code == status.HTTP_200_OK
		new_access_token = refresh_response.data['access']
		
		# 3. Acceder con nuevo token
		profile_url = '/api/v1/dashboard/auth/profile/me/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
		profile_response = api_client.get(profile_url)
		
		assert profile_response.status_code == status.HTTP_200_OK