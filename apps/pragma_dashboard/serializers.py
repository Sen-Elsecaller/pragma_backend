from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
	SesionSimulacion,
	ProgresoHistorico,
	DecisionTomada,
	EventoOcurrido,
	MetricaDesempeno,
	SaveFileUsuario,
	AnalisisIA
)


class UserSerializer(serializers.ModelSerializer):
	"""Serializador para el modelo User"""
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'first_name', 'last_name']
		read_only_fields = ['id']


class MetricaDesempenoSerializer(serializers.ModelSerializer):
	"""Serializador para las métricas de desempeño"""
	porcentaje_acierto = serializers.SerializerMethodField()

	class Meta:
		model = MetricaDesempeno
		fields = [
			'id',
			'sesion',
			'nivel_estres',
			'decisiones_acertadas',
			'decisiones_totales',
			'porcentaje_acierto',
			'tiempo_promedio_decision',
			'eventos_manejados',
			'timestamp_captura',
			'created_at'
		]
		read_only_fields = ['id', 'created_at', 'timestamp_captura']

	def get_porcentaje_acierto(self, obj):
		return obj.porcentaje_acierto


class DecisionTomadaSerializer(serializers.ModelSerializer):
	"""Serializador para las decisiones tomadas"""
	class Meta:
		model = DecisionTomada
		fields = [
			'id',
			'sesion',
			'decision_id',
			'tiempo_respuesta_segundos',
			'fue_acertada',
			'timestamp_decision',
			'created_at'
		]
		read_only_fields = ['id', 'created_at', 'timestamp_decision']


class EventoOcurridoSerializer(serializers.ModelSerializer):
	"""Serializador para los eventos ocurridos"""
	class Meta:
		model = EventoOcurrido
		fields = [
			'id',
			'sesion',
			'evento_id',
			'timestamp_ocurrencia',
			'fue_manejado_correctamente',
			'created_at'
		]
		read_only_fields = ['id', 'created_at']


class SesionSimulacionDetailSerializer(serializers.ModelSerializer):
	"""Serializador detallado para sesiones de simulación con relaciones"""
	decisiones = DecisionTomadaSerializer(many=True, read_only=True)
	eventos = EventoOcurridoSerializer(many=True, read_only=True)
	metricas = MetricaDesempenoSerializer(read_only=True)
	usuario = UserSerializer(read_only=True)

	class Meta:
		model = SesionSimulacion
		fields = [
			'id',
			'usuario',
			'escenario_nombre',
			'fecha_inicio',
			'fecha_fin',
			'duracion_segundos',
			'completada',
			'decisiones',
			'eventos',
			'metricas',
			'created_at',
			'updated_at'
		]
		read_only_fields = ['id', 'created_at', 'updated_at', 'fecha_inicio']


class SesionSimulacionListSerializer(serializers.ModelSerializer):
	"""Serializador simplificado para listas de sesiones"""
	usuario = UserSerializer(read_only=True)

	class Meta:
		model = SesionSimulacion
		fields = [
			'id',
			'usuario',
			'escenario_nombre',
			'fecha_inicio',
			'fecha_fin',
			'duracion_segundos',
			'completada',
			'created_at'
		]
		read_only_fields = ['id', 'created_at']


class SesionSimulacionCreateSerializer(serializers.ModelSerializer):
	"""Serializador para crear sesiones de simulación"""
	class Meta:
		model = SesionSimulacion
		fields = [
			'escenario_nombre',
			'duracion_segundos',
			'completada'
		]

	def create(self, validated_data):
		validated_data['usuario'] = self.context['request'].user
		return super().create(validated_data)


class ProgresoHistoricoSerializer(serializers.ModelSerializer):
	"""Serializador para el progreso histórico"""
	usuario = UserSerializer(read_only=True)

	class Meta:
		model = ProgresoHistorico
		fields = [
			'id',
			'usuario',
			'fecha_calculo',
			'promedio_estres',
			'sesiones_completadas',
			'tiempo_total_minutos',
			'escenarios_practicados',
			'created_at'
		]
		read_only_fields = ['id', 'created_at', 'fecha_calculo']


class SaveFileUsuarioSerializer(serializers.ModelSerializer):
	"""Serializador para archivos guardados de usuario"""
	usuario = UserSerializer(read_only=True)

	class Meta:
		model = SaveFileUsuario
		fields = [
			'id',
			'usuario',
			'datos_savefile',
			'ultima_actualizacion',
			'version_savefile',
			'created_at'
		]
		read_only_fields = ['id', 'created_at', 'ultima_actualizacion']

	def create(self, validated_data):
		validated_data['usuario'] = self.context['request'].user
		return super().create(validated_data)


class DashboardResumenSerializer(serializers.Serializer):
	"""Serializador para el resumen del dashboard personal"""
	total_sesiones = serializers.IntegerField()
	sesiones_completadas = serializers.IntegerField()
	tiempo_total_minutos = serializers.IntegerField()
	promedio_estres = serializers.FloatField()
	porcentaje_acierto_promedio = serializers.FloatField()
	escenarios_completados = serializers.IntegerField()
	nivel_progreso = serializers.CharField()


# ============================================
# AUTENTICACIÓN Y USUARIO
# ============================================


class UserRegistrationSerializer(serializers.ModelSerializer):
	"""Serializador para registro de nuevos usuarios"""
	password = serializers.CharField(
		write_only=True,
		required=True,
		min_length=8,
		help_text="Mínimo 8 caracteres"
	)
	password_confirm = serializers.CharField(
		write_only=True,
		required=True,
		min_length=8,
		help_text="Debe coincidir con password"
	)

	class Meta:
		model = User
		fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
		extra_kwargs = {
			'username': {'required': True, 'min_length': 3},
			'email': {'required': True},
		}

	def validate_username(self, value):
		"""Validar que el username sea único"""
		if User.objects.filter(username=value).exists():
			raise serializers.ValidationError('Este nombre de usuario ya está en uso')
		return value

	def validate_email(self, value):
		"""Validar que el email sea único"""
		if User.objects.filter(email=value).exists():
			raise serializers.ValidationError('Este email ya está registrado')
		return value

	def validate(self, data):
		"""Validar que las contraseñas coincidan"""
		if data['password'] != data['password_confirm']:
			raise serializers.ValidationError({
				'password_confirm': 'Las contraseñas no coinciden'
			})
		return data

	def create(self, validated_data):
		"""Crear usuario con contraseña hasheada"""
		validated_data.pop('password_confirm')
		user = User.objects.create_user(**validated_data)
		return user


class UserDetailSerializer(serializers.ModelSerializer):
	"""Serializador para detalles del usuario"""
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
		read_only_fields = ['id', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
	"""Serializador para cambiar contraseña"""
	old_password = serializers.CharField(write_only=True, required=True)
	new_password = serializers.CharField(write_only=True, required=True, min_length=8)
	new_password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)

	def validate(self, data):
		if data['new_password'] != data['new_password_confirm']:
			raise serializers.ValidationError({
				'new_password_confirm': 'Las contraseñas no coinciden'
			})
		return data


class AnalisisIASerializer(serializers.ModelSerializer):
	"""Serializador para análisis generados por IA"""
	class Meta:
		model = AnalisisIA
		fields = [
			'id',
			'sesion',
			'usuario',
			'puntuacion_total',
			'nivel_general',
			'emoji_nivel',
			'score_velocidad',
			'score_precision',
			'score_consistencia',
			'score_manejo_estres',
			'score_engagement',
			'resumen_fortalezas',
			'resumen_areas_mejora',
			'resumen_recomendaciones',
			'nivel_riesgo',
			'alertas_psicologicas',
			'requiere_intervencion',
			'url_grafico_distribucion',
			'url_grafico_radar',
			'url_grafico_indicadores',
			'datos_json',
			'fecha_analisis',
			'created_at'
		]
		read_only_fields = ['id', 'usuario', 'created_at', 'fecha_analisis']