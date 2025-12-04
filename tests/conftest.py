import os
import sys
import django
from pathlib import Path

import pytest
from django.conf import settings

# ✅ AGREGAR PATHS CORRECTAMENTE
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR

# Agregar ambas rutas al path
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(PROJECT_DIR))

# ✅ Configurar Django ANTES de cualquier import
def pytest_configure():
	"""Se ejecuta antes de cualquier cosa - CRÍTICO"""
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
	
	# Verificar que settings está configurado
	if not settings.configured:
		django.setup()
	
	print("✅ Django configurado correctamente")

# ============ FIXTURES - ENCRYPTION ============

@pytest.fixture
def encryption_key():
	"""Clave de cifrado válida (32 bytes = 256 bits)"""
	return b'a' * 32

@pytest.fixture
def invalid_encryption_key():
	"""Clave de cifrado INVÁLIDA (16 bytes)"""
	return b'b' * 16

@pytest.fixture
def test_data():
	"""Datos de prueba"""
	return {
		'simple': 'Usuario: john@example.com',
		'unicode': 'Datos con ñ, é, ü y 中文',
		'empty': '',
		'large': 'X' * 100000,
		'special_chars': '!@#$%^&*()_+-=[]{}|;:",.<>?/',
		'json_like': '{"id": 123, "email": "test@pragma.cl"}',
	}

# ============ FIXTURES - USUARIOS ============

@pytest.fixture
def user_data():
	"""Datos de usuario para pruebas"""
	return {
		'nombre': 'Juan Sebastian',
		'email': 'juan@pragma.cl',
		'password': 'TestPass123',
		'password_confirm': 'TestPass123'
	}

@pytest.fixture
def admin_user_data():
	"""Datos de usuario administrador"""
	return {
		'nombre': 'Admin User',
		'email': 'admin@pragma.cl',
		'password': 'AdminPass123',
		'password_confirm': 'AdminPass123'
	}

@pytest.fixture
def django_user(db):
	"""Crear usuario de prueba en BD"""
	from django.contrib.auth.models import User
	return User.objects.create_user(
		username='testuser',
		email='test@pragma.cl',
		password='TestPass123'
	)

@pytest.fixture
def registered_user(db, user_data):
	"""Crear usuario registrado en BD"""
	from django.contrib.auth.models import User
	user = User.objects.create_user(
		username='juan',
		email=user_data['email'],
		password=user_data['password'],
		first_name='Juan',
		last_name='Sebastian'
	)
	return user

@pytest.fixture
def admin_user(db, admin_user_data):
	"""Crear usuario admin en BD"""
	from django.contrib.auth.models import User
	admin = User.objects.create_superuser(
		username='admin',
		email=admin_user_data['email'],
		password=admin_user_data['password'],
		first_name='Admin',
		last_name='User'
	)
	return admin

@pytest.fixture
def django_admin_user(db):
	"""Crear usuario admin de prueba (alias)"""
	from django.contrib.auth.models import User
	user = User.objects.create_user(
		username='admin',
		email='admin@pragma.cl',
		password='Admin@2024'
	)
	user.is_staff = True
	user.is_superuser = True
	user.save()
	return user

# ============ FIXTURES - JWT TOKENS ============

@pytest.fixture
def access_token(registered_user):
	"""Generar token JWT válido"""
	from rest_framework_simplejwt.tokens import RefreshToken
	refresh = RefreshToken.for_user(registered_user)
	return str(refresh.access_token)

@pytest.fixture
def refresh_token(registered_user):
	"""Generar refresh token válido"""
	from rest_framework_simplejwt.tokens import RefreshToken
	refresh = RefreshToken.for_user(registered_user)
	return str(refresh)

# ============ FIXTURES - API CLIENT ============

@pytest.fixture
def api_client():
	"""Cliente REST para pruebas de API"""
	from rest_framework.test import APIClient
	return APIClient()

@pytest.fixture
def authenticated_client(api_client, registered_user):
	"""Cliente REST autenticado"""
	api_client.force_authenticate(user=registered_user)
	return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
	"""Cliente REST autenticado como admin"""
	api_client.force_authenticate(user=admin_user)
	return api_client

# ============ FIXTURES - PU-002 MÉTRICAS (GODOT SAVEFILE) ============

@pytest.fixture
def godot_savefile_json():
	"""JSON que llega desde Godot con estructura completa"""
	return {
		"notas": [{
			"scenario_name": "Sala de clases",
			"emotion": "bad",
			"question": "¿Como estas hablando?",
			"selected_response": "Rapido, quiero que esto termine rapido.",
			"outcome_text": "Los nervios empeoran",
			"feedback": "Hablar mas rapido solo te pondra mas nervioso. Toma pausas, recuerda respirar.",
			"response_time": 14.5994160000002
		}],
		"sesiones": [{
			"timestamp_inicio": "2025-11-19T11:37:05",
			"timestamp_fin": "2025-11-19T11:38:08",
			"decisiones": [
				{
					"scenario_name": "Sala de clases",
					"emotion": "bad",
					"question": "¿Que haces mientras esperas?",
					"selected_response": "Mi mente divaga",
					"outcome_text": "Los nervios empeoran",
					"feedback": "Dejar los pensamientos correr libremente en situaciones de ansiedad es una invitacion al malestar",
					"response_time": 0.816634
				},
				{
					"scenario_name": "Sala de clases",
					"emotion": "good",
					"question": "¿Que haces mientras esperas?",
					"selected_response": "Voy a repasar la materia",
					"outcome_text": "Te sientes mas en control",
					"feedback": "Repasar puede ayudar a algunas personas a calmarse",
					"response_time": 1.74993
				},
				{
					"scenario_name": "Sala de clases",
					"emotion": "",
					"question": "Pasas adelante",
					"selected_response": "Presento de inmediato, apresuradamente.",
					"outcome_text": "Empiezas tartamudeando",
					"feedback": "Aunque la situacion pueda ser dificil, tu siempre tienes el control.",
					"response_time": 4.41648999999998
				},
				{
					"scenario_name": "Sala de clases",
					"emotion": "good",
					"question": "¿Que es lo primero que se te pasa por la cabeza?",
					"selected_response": "Concentrarme en mi presentacion.",
					"outcome_text": "Te concentras en tu presentacion",
					"feedback": "Enfocarse en los demas seria un error.",
					"response_time": 6.2165233333333
				},
				{
					"scenario_name": "Sala de clases",
					"emotion": "bad",
					"question": "¿Como estas hablando?",
					"selected_response": "Rapido, quiero que esto termine rapido.",
					"outcome_text": "Los nervios empeoran",
					"feedback": "Hablar mas rapido solo te pondra mas nervioso.",
					"response_time": 14.5994160000002
				},
				{
					"scenario_name": "Sala de clases",
					"emotion": "good",
					"question": "El profesor pone cara de duda",
					"selected_response": "Lo ignoro",
					"outcome_text": "Te concentras en tu presentacion",
					"feedback": "Mantener el flujo de la presentacion es lo importante.",
					"response_time": 1.849926
				}
			]
		}],
		"user_data": {
			"nombre": "Gerald"
		}
	}

@pytest.fixture
def authenticated_user(db):
	"""Usuario autenticado que sube el savefile (PU-002)"""
	from django.contrib.auth.models import User
	user = User.objects.create_user(
		username='godot_user',
		email='godot@pragma.cl',
		password='GodotPass123'
	)
	return user

@pytest.fixture
def authenticated_token(authenticated_user):
	"""Token JWT para usuario autenticado (PU-002)"""
	from rest_framework_simplejwt.tokens import RefreshToken
	refresh = RefreshToken.for_user(authenticated_user)
	return str(refresh.access_token)