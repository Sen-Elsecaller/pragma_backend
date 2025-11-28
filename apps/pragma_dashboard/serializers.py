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


# ============================================
# ANÁLISIS IA - NUEVOS SERIALIZADORES
# ============================================

class AnalisisIAListSerializer(serializers.ModelSerializer):
	"""Serializador simplificado para listas de análisis - INCLUYE CAMPOS DE COMPETENCIAS"""
	usuario = UserSerializer(read_only=True)

	class Meta:
		model = AnalisisIA
		fields = [
			'id',
			'savefile_id',
			'usuario',
			'usuario_nombre',
			'usuario_email',
			'resumen_ejecutivo',
			'conclusiones_clinicas',
			'alertas_psicologicas',
			'nivel_riesgo',
			'requiere_intervencion',
			'timestamp_analisis',
			'created_at',
			# ✅ AGREGADOS - Campos de competencias y análisis
			'perfil_psicoeducativo',
			'mecanismos_afrontamiento',
			'metadata_groq',
			'analisis_detallado'
		]
		read_only_fields = ['id', 'created_at', 'timestamp_analisis']


class AnalisisIADetailSerializer(serializers.ModelSerializer):
	"""Serializador detallado para análisis completos"""
	usuario = UserSerializer(read_only=True)

	class Meta:
		model = AnalisisIA
		fields = [
			'id',
			'sesion',
			'savefile_id',
			'usuario',
			'usuario_nombre',
			'usuario_email',
			
			# Retroalimentación principal
			'resumen_ejecutivo',
			'conclusiones_clinicas',
			'alertas_psicologicas',
			
			# Análisis estructurado
			'perfil_psicoeducativo',
			'analisis_detallado',
			'mecanismos_afrontamiento',
			'indicadores_psicologicos',
			'recomendaciones_especificas',
			'plan_intervencion',
			
			# Visualización
			'graficos',
			
			# Nivel de riesgo
			'nivel_riesgo',
			'requiere_intervencion',
			
			# Metadata
			'metadata_groq',
			'timestamp_analisis',
			'timestamp_recibido',
			'created_at',
			'updated_at'
		]
		read_only_fields = [
			'id', 'created_at', 'updated_at', 
			'timestamp_analisis', 'timestamp_recibido'
		]


class AnalisisIACreateSerializer(serializers.ModelSerializer):
	"""Serializador para crear análisis (recibido de N8N)"""
	usuario_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
	
	class Meta:
		model = AnalisisIA
		fields = [
			'sesion',
			'savefile_id',
			'usuario_id',  # ← Aceptar como integer, no como relación
			'usuario_nombre',
			'usuario_email',
			
			'resumen_ejecutivo',
			'conclusiones_clinicas',
			'alertas_psicologicas',
			
			'perfil_psicoeducativo',
			'analisis_detallado',
			'mecanismos_afrontamiento',
			'indicadores_psicologicos',
			'recomendaciones_especificas',
			'plan_intervencion',
			
			'graficos',
			'metadata_groq',
			'datos_completos_groq',
			
			'nivel_riesgo',
			'requiere_intervencion',
			'timestamp_analisis',
		]

	def create(self, validated_data):
		"""Crear análisis desde N8N - Buscar usuario por ID"""
		usuario_id = validated_data.pop('usuario_id', None)
		
		if usuario_id:
			try:
				usuario = User.objects.get(id=usuario_id)
				validated_data['usuario'] = usuario
				print(f'✅ Usuario encontrado: {usuario.username} (ID: {usuario_id})')
			except User.DoesNotExist:
				print(f'⚠️ Usuario ID {usuario_id} no encontrado')
		
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
	"""
	Serializador para registro de nuevos usuarios
	Campos: nombre (Nombre completo), email, password, password_confirm
	El nombre se divide en first_name y last_name automáticamente
	"""
	nombre = serializers.CharField(
		write_only=True,
		required=True,
		min_length=3,
		help_text="Nombre completo del usuario"
	)
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
		fields = ['nombre', 'email', 'password', 'password_confirm']
		extra_kwargs = {
			'email': {'required': True},
		}

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
		
		# Dividir nombre en first_name y last_name
		nombre = validated_data.pop('nombre')
		partes_nombre = nombre.strip().split(maxsplit=1)
		
		first_name = partes_nombre[0] if len(partes_nombre) > 0 else ''
		last_name = partes_nombre[1] if len(partes_nombre) > 1 else ''
		
		# Generar username desde el email (sin dominio)
		email = validated_data['email']
		username = email.split('@')[0]
		
		# Si el username ya existe, agregar un número
		counter = 1
		original_username = username
		while User.objects.filter(username=username).exists():
			username = f"{original_username}{counter}"
			counter += 1
		
		# Preparar datos para crear usuario
		validated_data['username'] = username
		validated_data['first_name'] = first_name
		validated_data['last_name'] = last_name
		
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