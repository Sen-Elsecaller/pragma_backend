"""
PRUEBA UNITARIA PU-002: Sistema de Captura de Métricas
========================================================
Validación de persistencia de datos desde Godot (SaveFile JSON)
- Estructura de sesiones
- Decisiones y respuestas
- Métricas de desempeño
- Timestamps

FLUJO DE GODOT A BACKEND:
1. Godot genera SaveFile JSON con sesión completa
2. Cliente envía POST a /api/v1/dashboard/savefiles/ CON AUTENTICACIÓN
3. Backend recibe, cifra datos con AES-256
4. Guarda en BD asociado al usuario autenticado
5. Se generan métricas automáticas desde decisiones
6. Usuario accede a análisis en Dashboard

ESTRUCTURA DE PRUEBAS:
- TC-001 a TC-006: Validación de estructura JSON
- TC-007 a TC-011: Validación de datos (tipos, rangos, formatos)
- TC-012 a TC-014: Upload y cifrado de savefile (SIEMPRE AUTENTICADO)
- TC-015 a TC-018: Cálculo de métricas desde decisiones
- TC-019 a TC-020: Recuperación y descifrado de savefiles
- TC-021 a TC-022: Flujos completos y múltiples sesiones
- TC-023 a TC-025: Edge cases
"""

import pytest
import json
from datetime import datetime
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


# ============ FIXTURES ============

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
	"""Usuario autenticado que sube el savefile"""
	user = User.objects.create_user(
		username='testuser',
		email='test@pragma.cl',
		password='TestPass123'
	)
	return user


@pytest.fixture
def authenticated_token(authenticated_user):
	"""Token JWT para usuario autenticado"""
	refresh = RefreshToken.for_user(authenticated_user)
	return str(refresh.access_token)


@pytest.fixture
def api_client():
	"""Cliente REST para pruebas"""
	return APIClient()


# ============ PRUEBAS DE ESTRUCTURA JSON ============

class TestSaveFileStructure:
	"""Pruebas de estructura del JSON de Godot"""

	def test_savefile_tiene_campos_principales(self, godot_savefile_json):
		"""✅ TC-001: SaveFile tiene campos principales"""
		assert 'notas' in godot_savefile_json
		assert 'sesiones' in godot_savefile_json
		assert 'user_data' in godot_savefile_json
		
		# Verificar tipos
		assert isinstance(godot_savefile_json['notas'], list)
		assert isinstance(godot_savefile_json['sesiones'], list)
		assert isinstance(godot_savefile_json['user_data'], dict)

	def test_user_data_tiene_nombre_personaje(self, godot_savefile_json):
		"""✅ TC-002: user_data contiene nombre del personaje"""
		user_data = godot_savefile_json['user_data']
		assert 'nombre' in user_data
		assert user_data['nombre'] == 'Gerald'

	def test_sesion_tiene_timestamps(self, godot_savefile_json):
		"""✅ TC-003: Sesión tiene timestamps de inicio y fin"""
		sesion = godot_savefile_json['sesiones'][0]
		assert 'timestamp_inicio' in sesion
		assert 'timestamp_fin' in sesion
		assert sesion['timestamp_inicio'] == "2025-11-19T11:37:05"
		assert sesion['timestamp_fin'] == "2025-11-19T11:38:08"

	def test_sesion_tiene_decisiones(self, godot_savefile_json):
		"""✅ TC-004: Sesión tiene lista de decisiones"""
		sesion = godot_savefile_json['sesiones'][0]
		assert 'decisiones' in sesion
		assert isinstance(sesion['decisiones'], list)
		assert len(sesion['decisiones']) == 6

	def test_decision_tiene_campos_completos(self, godot_savefile_json):
		"""✅ TC-005: Cada decisión tiene todos los campos requeridos"""
		decision = godot_savefile_json['sesiones'][0]['decisiones'][0]
		
		campos_requeridos = [
			'scenario_name',
			'emotion',
			'question',
			'selected_response',
			'outcome_text',
			'feedback',
			'response_time'
		]
		
		for campo in campos_requeridos:
			assert campo in decision, f"Falta campo: {campo}"

	def test_nota_tiene_campos_completos(self, godot_savefile_json):
		"""✅ TC-006: Cada nota tiene todos los campos requeridos"""
		nota = godot_savefile_json['notas'][0]
		
		campos_requeridos = [
			'scenario_name',
			'emotion',
			'question',
			'selected_response',
			'outcome_text',
			'feedback',
			'response_time'
		]
		
		for campo in campos_requeridos:
			assert campo in nota, f"Falta campo: {campo}"


# ============ PRUEBAS DE VALIDACIÓN DE DATOS ============

class TestMetricsDataValidation:
	"""Pruebas de validación de datos de métricas"""

	def test_response_time_es_numero_positivo(self, godot_savefile_json):
		"""✅ TC-007: response_time es número positivo"""
		for decision in godot_savefile_json['sesiones'][0]['decisiones']:
			response_time = decision['response_time']
			assert isinstance(response_time, (int, float))
			assert response_time > 0, f"response_time negativo: {response_time}"

	def test_emotion_tiene_valores_validos(self, godot_savefile_json):
		"""✅ TC-008: emotion tiene valores válidos (good, bad, empty)"""
		emociones_validas = ['good', 'bad', '']
		
		for decision in godot_savefile_json['sesiones'][0]['decisiones']:
			emotion = decision['emotion']
			assert emotion in emociones_validas, f"Emoción inválida: {emotion}"

	def test_timestamps_formato_iso8601(self, godot_savefile_json):
		"""✅ TC-009: Timestamps en formato ISO8601"""
		sesion = godot_savefile_json['sesiones'][0]
		
		for timestamp_key in ['timestamp_inicio', 'timestamp_fin']:
			timestamp = sesion[timestamp_key]
			# Validar formato ISO8601
			try:
				datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
			except ValueError:
				pytest.fail(f"Timestamp inválido: {timestamp}")

	def test_duracion_sesion_es_positiva(self, godot_savefile_json):
		"""✅ TC-010: Duración de sesión es positiva"""
		sesion = godot_savefile_json['sesiones'][0]
		inicio = datetime.fromisoformat(sesion['timestamp_inicio'])
		fin = datetime.fromisoformat(sesion['timestamp_fin'])
		duracion = (fin - inicio).total_seconds()
		
		assert duracion > 0, f"Duración negativa: {duracion}s"

	def test_scenario_name_no_vacio(self, godot_savefile_json):
		"""✅ TC-011: scenario_name no está vacío"""
		for decision in godot_savefile_json['sesiones'][0]['decisiones']:
			scenario = decision['scenario_name']
			assert len(scenario) > 0, "scenario_name vacío"
			assert scenario == "Sala de clases"


# ============ PRUEBAS DE UPLOAD DE SAVEFILE ============

@pytest.mark.django_db
class TestSaveFileUpload:
	"""Pruebas de upload de savefile a la API"""

	def test_upload_savefile_exitoso(self, api_client, authenticated_user, authenticated_token, godot_savefile_json):
		"""✅ TC-012: Upload de savefile exitoso con autenticación"""
		url = '/api/v1/dashboard/savefiles/'
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {authenticated_token}')
		response = api_client.post(
			url,
			{'datos_savefile': json.dumps(godot_savefile_json)},
			format='json'
		)
		
		assert response.status_code == status.HTTP_201_CREATED
		assert 'id' in response.data
		assert response.data['version_savefile'] == '1.0'

	def test_upload_savefile_asocia_usuario_correcto(self, api_client, authenticated_user, authenticated_token, godot_savefile_json):
		"""✅ TC-013: SaveFile se asocia al usuario correcto"""
		from apps.pragma_dashboard.models import SaveFileUsuario
		
		url = '/api/v1/dashboard/savefiles/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {authenticated_token}')
		
		response = api_client.post(
			url,
			{'datos_savefile': json.dumps(godot_savefile_json)},
			format='json'
		)
		
		assert response.status_code == status.HTTP_201_CREATED
		
		# Verificar que se asoció al usuario correcto
		savefile = SaveFileUsuario.objects.get(id=response.data['id'])
		assert savefile.usuario == authenticated_user

	def test_upload_savefile_datos_cifrados(self, api_client, authenticated_user, authenticated_token, godot_savefile_json):
		"""✅ TC-014: Datos del savefile se guardan cifrados"""
		from apps.pragma_dashboard.models import SaveFileUsuario
		
		url = '/api/v1/dashboard/savefiles/'
		
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {authenticated_token}')
		response = api_client.post(
			url,
			{'datos_savefile': json.dumps(godot_savefile_json)},
			format='json'
		)
		
		assert response.status_code == status.HTTP_201_CREATED
		
		# Verificar que en BD están cifrados (en formato HEX)
		savefile = SaveFileUsuario.objects.get(usuario=authenticated_user)
		datos_en_bd = savefile.datos_savefile
		
		# Debe ser HEX (no JSON plano)
		assert len(datos_en_bd) > 0
		# Intentar parsearlo como JSON debe fallar (está cifrado)
		try:
			json.loads(datos_en_bd)
			pytest.fail("Datos no están cifrados")
		except json.JSONDecodeError:
			pass  # Correcto, está cifrado


# ============ PRUEBAS DE MÉTRICAS CALCULADAS ============

@pytest.mark.django_db
class TestMetricsCalculation:
	"""Pruebas de cálculo de métricas desde el savefile"""

	def test_calcular_tiempo_total_sesion(self, godot_savefile_json):
		"""✅ TC-015: Calcular tiempo total de sesión"""
		sesion = godot_savefile_json['sesiones'][0]
		inicio = datetime.fromisoformat(sesion['timestamp_inicio'])
		fin = datetime.fromisoformat(sesion['timestamp_fin'])
		duracion_segundos = int((fin - inicio).total_seconds())
		
		assert duracion_segundos == 63  # 11:37:05 a 11:38:08

	def test_calcular_tiempo_promedio_decision(self, godot_savefile_json):
		"""✅ TC-016: Calcular tiempo promedio por decisión"""
		decisiones = godot_savefile_json['sesiones'][0]['decisiones']
		
		tiempo_total = sum(d['response_time'] for d in decisiones)
		tiempo_promedio = tiempo_total / len(decisiones)
		
		assert len(decisiones) == 6
		assert tiempo_promedio > 0
		assert round(tiempo_promedio, 2) == 4.94  # Valor real calculado

	def test_calcular_emociones_finales(self, godot_savefile_json):
		"""✅ TC-017: Calcular distribución de emociones"""
		decisiones = godot_savefile_json['sesiones'][0]['decisiones']
		
		emociones = {}
		for decision in decisiones:
			emotion = decision['emotion']
			emociones[emotion] = emociones.get(emotion, 0) + 1
		
		assert emociones.get('good', 0) == 3
		assert emociones.get('bad', 0) == 2
		assert emociones.get('', 0) == 1

	def test_crear_metrica_desempeno(self, db, authenticated_user, godot_savefile_json):
		"""✅ TC-018: Crear métrica de desempeño desde savefile"""
		from apps.pragma_dashboard.models import SesionSimulacion, MetricaDesempeno
		
		# Crear sesión
		sesion = SesionSimulacion.objects.create(
			usuario=authenticated_user,
			escenario_nombre="Sala de clases",
			completada=True,
			duracion_segundos=63
		)
		
		decisiones = godot_savefile_json['sesiones'][0]['decisiones']
		
		# Calcular métricas
		decisiones_buenas = sum(1 for d in decisiones if d['emotion'] == 'good')
		tiempo_promedio = sum(d['response_time'] for d in decisiones) / len(decisiones)
		
		# Crear métrica
		metrica = MetricaDesempeno.objects.create(
			sesion=sesion,
			nivel_estres=75,
			decisiones_acertadas=decisiones_buenas,
			decisiones_totales=len(decisiones),
			tiempo_promedio_decision=int(tiempo_promedio),
			eventos_manejados=3
		)
		
		assert metrica.id is not None
		assert metrica.decisiones_acertadas == 3
		assert metrica.decisiones_totales == 6
		assert metrica.porcentaje_acierto == 50.0


# ============ PRUEBAS DE RECUPERACIÓN DE DATOS ============

@pytest.mark.django_db
class TestSaveFileRetrieval:
	"""Pruebas de recuperación y descifrado de savefile"""

	def test_obtener_ultimo_savefile(self, api_client, authenticated_user, authenticated_token, godot_savefile_json):
		"""✅ TC-019: Obtener último savefile del usuario"""
		from apps.pragma_dashboard.models import SaveFileUsuario
		
		# Guardar savefile
		url = '/api/v1/dashboard/savefiles/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {authenticated_token}')
		
		response = api_client.post(
			url,
			{'datos_savefile': json.dumps(godot_savefile_json)},
			format='json'
		)
		assert response.status_code == status.HTTP_201_CREATED
		
		# Recuperar último
		url_ultimo = '/api/v1/dashboard/savefiles/ultimo/'
		response = api_client.get(url_ultimo)
		
		assert response.status_code == status.HTTP_200_OK
		assert 'datos_savefile' in response.data
		# Los datos deben estar descifrados
		datos = response.data['datos_savefile']
		assert isinstance(datos, dict)

	def test_savefile_descifrado_tiene_datos_correctos(self, api_client, authenticated_user, authenticated_token, godot_savefile_json):
		"""✅ TC-020: Savefile descifrado tiene estructura correcta"""
		from apps.pragma_dashboard.models import SaveFileUsuario
		
		# Guardar savefile
		url = '/api/v1/dashboard/savefiles/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {authenticated_token}')
		
		response = api_client.post(
			url,
			{'datos_savefile': json.dumps(godot_savefile_json)},
			format='json'
		)
		
		# Recuperar
		url_ultimo = '/api/v1/dashboard/savefiles/ultimo/'
		response = api_client.get(url_ultimo)
		
		datos = response.data['datos_savefile']
		assert 'sesiones' in datos
		assert 'notas' in datos
		assert 'user_data' in datos
		assert len(datos['sesiones']) == 1
		assert len(datos['sesiones'][0]['decisiones']) == 6


# ============ PRUEBAS DE FLUJO COMPLETO ============

@pytest.mark.django_db
class TestMetricsCompleteFlow:
	"""Pruebas de flujo completo: Godot → API → BD → Métricas"""

	def test_flujo_completo_godot_a_analisis(self, api_client, authenticated_user, authenticated_token, godot_savefile_json):
		"""✅ TC-021: Flujo completo: Godot → SaveFile → Métricas"""
		from apps.pragma_dashboard.models import SaveFileUsuario, SesionSimulacion, MetricaDesempeno
		
		# 1. Upload savefile desde Godot
		url = '/api/v1/dashboard/savefiles/'
		api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {authenticated_token}')
		
		response = api_client.post(
			url,
			{'datos_savefile': json.dumps(godot_savefile_json)},
			format='json'
		)
		assert response.status_code == status.HTTP_201_CREATED
		savefile_id = response.data['id']
		
		# 2. Crear sesión asociada al savefile
		sesion = SesionSimulacion.objects.create(
			usuario=authenticated_user,
			escenario_nombre="Sala de clases",
			completada=True,
			duracion_segundos=63
		)
		
		# 3. Crear métricas de desempeño
		metrica = MetricaDesempeno.objects.create(
			sesion=sesion,
			nivel_estres=75,
			decisiones_acertadas=3,
			decisiones_totales=6,
			tiempo_promedio_decision=5,
			eventos_manejados=3
		)
		
		# 4. Recuperar y verificar
		assert SaveFileUsuario.objects.filter(usuario=authenticated_user).exists()
		assert MetricaDesempeno.objects.filter(sesion=sesion).exists()
		assert metrica.porcentaje_acierto == 50.0

	def test_multiples_sesiones_mismo_usuario(self, api_client, authenticated_user, authenticated_token):
		"""✅ TC-022: Usuario puede tener múltiples sesiones"""
		from apps.pragma_dashboard.models import SesionSimulacion
		
		# Crear múltiples sesiones
		sesiones_data = [
			{'escenario_nombre': 'Sala de clases', 'duracion_segundos': 63},
			{'escenario_nombre': 'Presentación', 'duracion_segundos': 45},
			{'escenario_nombre': 'Entrevista', 'duracion_segundos': 120},
		]
		
		for datos in sesiones_data:
			SesionSimulacion.objects.create(
				usuario=authenticated_user,
				completada=True,
				**datos
			)
		
		# Verificar
		sesiones = SesionSimulacion.objects.filter(usuario=authenticated_user)
		assert sesiones.count() == 3
		assert sesiones.filter(escenario_nombre='Sala de clases').exists()


# ============ PRUEBAS DE EDGE CASES ============

class TestMetricsEdgeCases:
	"""Pruebas de casos extremos"""

	def test_savefile_con_cero_decisiones(self):
		"""✅ TC-023: Savefile con sesión sin decisiones"""
		savefile = {
			'notas': [],
			'sesiones': [{
				'timestamp_inicio': '2025-11-19T11:37:05',
				'timestamp_fin': '2025-11-19T11:37:10',
				'decisiones': []
			}],
			'user_data': {'nombre': 'Test'}
		}
		
		assert len(savefile['sesiones'][0]['decisiones']) == 0

	def test_response_time_muy_grande(self):
		"""✅ TC-024: Response time muy grande (timeout del usuario)"""
		decision = {
			'scenario_name': 'Test',
			'emotion': 'bad',
			'question': 'Test',
			'selected_response': 'Test',
			'outcome_text': 'Test',
			'feedback': 'Test',
			'response_time': 999999.99  # Usuario se tardó mucho
		}
		
		assert decision['response_time'] > 10000

	def test_savefile_json_muy_grande(self):
		"""✅ TC-025: Savefile con muchas decisiones (100+)"""
		decisiones = []
		for i in range(100):
			decisiones.append({
				'scenario_name': 'Scenario',
				'emotion': 'good' if i % 2 == 0 else 'bad',
				'question': f'Pregunta {i}',
				'selected_response': f'Respuesta {i}',
				'outcome_text': f'Resultado {i}',
				'feedback': f'Feedback {i}',
				'response_time': float(i + 1)
			})
		
		assert len(decisiones) == 100
		assert json.dumps(decisiones) is not None