from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class SesionSimulacion(models.Model):
	"""
	Modelo que representa una sesión de simulación de un usuario.
	Relacionado con la tabla sesiones_simulacion del diagrama DER.
	"""
	usuario = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='sesiones_simulacion'
	)
	escenario_nombre = models.CharField(
		max_length=100,
		help_text="Nombre del escenario simulado"
	)
	fecha_inicio = models.DateTimeField(
		auto_now_add=True,
		help_text="Fecha y hora de inicio de la sesión"
	)
	fecha_fin = models.DateTimeField(
		null=True,
		blank=True,
		help_text="Fecha y hora de fin de la sesión"
	)
	duracion_segundos = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Duración total de la sesión en segundos"
	)
	completada = models.BooleanField(
		default=False,
		help_text="Indica si la sesión fue completada"
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-fecha_inicio']
		indexes = [
			models.Index(fields=['usuario', '-fecha_inicio']),
			models.Index(fields=['completada']),
		]
		verbose_name = "Sesión de Simulación"
		verbose_name_plural = "Sesiones de Simulación"

	def __str__(self):
		return f"Sesión {self.escenario_nombre} - {self.usuario.username}"


class ProgresoHistorico(models.Model):
	"""
	Modelo que registra el progreso histórico de un usuario.
	Relacionado con la tabla progreso_historico del diagrama DER.
	"""
	usuario = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='progreso_historico'
	)
	fecha_calculo = models.DateField(
		auto_now_add=True,
		help_text="Fecha del cálculo de progreso"
	)
	promedio_estres = models.DecimalField(
		max_digits=4,
		decimal_places=2,
		validators=[MinValueValidator(0), MaxValueValidator(100)],
		help_text="Promedio de estrés en escala 0-100"
	)
	sesiones_completadas = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Cantidad de sesiones completadas"
	)
	tiempo_total_minutos = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Tiempo total invertido en minutos"
	)
	escenarios_practicados = models.CharField(
		max_length=255,
		blank=True,
		help_text="Lista de escenarios practicados"
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-fecha_calculo']
		indexes = [
			models.Index(fields=['usuario', '-fecha_calculo']),
		]
		verbose_name = "Progreso Histórico"
		verbose_name_plural = "Progresos Históricos"

	def __str__(self):
		return f"Progreso {self.usuario.username} - {self.fecha_calculo}"


class DecisionTomada(models.Model):
	"""
	Modelo que registra las decisiones tomadas durante una sesión.
	Relacionado con la tabla decisiones_tomadas del diagrama DER.
	"""
	sesion = models.ForeignKey(
		SesionSimulacion,
		on_delete=models.CASCADE,
		related_name='decisiones'
	)
	decision_id = models.CharField(
		max_length=100,
		help_text="Identificador único de la decisión en el escenario"
	)
	tiempo_respuesta_segundos = models.IntegerField(
		validators=[MinValueValidator(0)],
		help_text="Tiempo que tardó el usuario en responder"
	)
	fue_acertada = models.BooleanField(
		help_text="Indica si la decisión fue correcta"
	)
	timestamp_decision = models.DateTimeField(
		auto_now_add=True,
		help_text="Momento exacto en que se tomó la decisión"
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-timestamp_decision']
		indexes = [
			models.Index(fields=['sesion', '-timestamp_decision']),
			models.Index(fields=['fue_acertada']),
		]
		verbose_name = "Decisión Tomada"
		verbose_name_plural = "Decisiones Tomadas"

	def __str__(self):
		return f"Decisión {self.decision_id} - {'Correcta' if self.fue_acertada else 'Incorrecta'}"


class EventoOcurrido(models.Model):
	"""
	Modelo que registra eventos que ocurrieron durante una sesión.
	Relacionado con la tabla eventos_ocurridos del diagrama DER.
	"""
	sesion = models.ForeignKey(
		SesionSimulacion,
		on_delete=models.CASCADE,
		related_name='eventos'
	)
	evento_id = models.CharField(
		max_length=100,
		help_text="Identificador único del evento"
	)
	timestamp_ocurrencia = models.DateTimeField(
		help_text="Momento en que ocurrió el evento"
	)
	fue_manejado_correctamente = models.BooleanField(
		help_text="Indica si el evento fue manejado correctamente"
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-timestamp_ocurrencia']
		indexes = [
			models.Index(fields=['sesion', '-timestamp_ocurrencia']),
			models.Index(fields=['fue_manejado_correctamente']),
		]
		verbose_name = "Evento Ocurrido"
		verbose_name_plural = "Eventos Ocurridos"

	def __str__(self):
		return f"Evento {self.evento_id} - {self.timestamp_ocurrencia}"


class MetricaDesempeno(models.Model):
	"""
	Modelo que almacena las métricas de desempeño de una sesión.
	Relacionado con la tabla metricas_desempeno del diagrama DER.
	"""
	sesion = models.OneToOneField(
		SesionSimulacion,
		on_delete=models.CASCADE,
		related_name='metricas'
	)
	nivel_estres = models.IntegerField(
		validators=[MinValueValidator(0), MaxValueValidator(100)],
		help_text="Nivel de estrés final (0-100)"
	)
	decisiones_acertadas = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Cantidad de decisiones acertadas"
	)
	decisiones_totales = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Cantidad total de decisiones tomadas"
	)
	tiempo_promedio_decision = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Tiempo promedio de respuesta en segundos"
	)
	eventos_manejados = models.IntegerField(
		default=0,
		validators=[MinValueValidator(0)],
		help_text="Cantidad de eventos manejados correctamente"
	)
	timestamp_captura = models.DateTimeField(
		auto_now_add=True,
		help_text="Momento en que se capturaron las métricas"
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Métrica de Desempeño"
		verbose_name_plural = "Métricas de Desempeño"

	def __str__(self):
		return f"Métricas - {self.sesion.escenario_nombre}"

	@property
	def porcentaje_acierto(self):
		"""Calcula el porcentaje de acierto en decisiones"""
		if self.decisiones_totales == 0:
			return 0
		return round((self.decisiones_acertadas / self.decisiones_totales) * 100, 2)


class SaveFileUsuario(models.Model):
	"""
	Modelo que almacena archivos guardados por usuarios.
	Relacionado con la tabla savefiles_usuario del diagrama DER.
	"""
	usuario = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='savefiles'
	)
	datos_savefile = models.TextField(
		help_text="Datos del archivo guardado en JSON o formato específico"
	)
	ultima_actualizacion = models.DateTimeField(
		auto_now=True,
		help_text="Última fecha de actualización"
	)
	version_savefile = models.CharField(
		max_length=20,
		default='1.0',
		help_text="Versión del formato del savefile"
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-ultima_actualizacion']
		indexes = [
			models.Index(fields=['usuario', '-ultima_actualizacion']),
		]
		verbose_name = "Archivo Guardado de Usuario"
		verbose_name_plural = "Archivos Guardados de Usuario"

	def __str__(self):
		return f"SaveFile - {self.usuario.username} ({self.version_savefile})"


class AnalisisIA(models.Model):
	NIVEL_RIESGO_CHOICES = [
		('bajo', 'Bajo'),
		('medio', 'Medio'),
		('alto', 'Alto'),
	]
	
	# Referencias a tablas externas (savefiles_usuario y usuarios)
	savefile_id = models.IntegerField(
		help_text="ID del savefiles_usuario",
		db_index=True
	)
	usuario_id = models.IntegerField(
		help_text="ID del usuario (referencia externa)"
	)
	
	# Puntuación general
	puntuacion_total = models.IntegerField(
		default=0,
		help_text="Puntuación total (0-100)"
	)
	nivel_general = models.CharField(
		max_length=50,
		default='Regular',
		choices=[
			('Excelente', 'Excelente'),
			('Bueno', 'Bueno'),
			('Regular', 'Regular'),
			('Necesita mejorar', 'Necesita mejorar'),
			('Crítico', 'Crítico'),
		]
	)
	emoji_nivel = models.CharField(
		max_length=10,
		default='⚠️'
	)
	
	# Scores de competencias (0-10)
	score_velocidad = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		default=0,
		help_text="Score de velocidad de respuesta (0-10)"
	)
	score_precision = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		default=0,
		help_text="Score de precisión (0-10)"
	)
	score_consistencia = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		default=0,
		help_text="Score de consistencia (0-10)"
	)
	score_manejo_estres = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		default=0,
		help_text="Score de manejo de estrés (0-10)"
	)
	score_engagement = models.DecimalField(
		max_digits=3,
		decimal_places=1,
		default=0,
		help_text="Score de engagement (0-10)"
	)
	
	# Análisis textual de Groq (como JSON strings)
	resumen_fortalezas = models.TextField(
		blank=True,
		default='[]',
		help_text="JSON array de fortalezas identificadas"
	)
	resumen_areas_mejora = models.TextField(
		blank=True,
		default='[]',
		help_text="JSON array de áreas de mejora"
	)
	resumen_recomendaciones = models.TextField(
		blank=True,
		default='[]',
		help_text="JSON array de recomendaciones"
	)
	
	# Indicadores de riesgo
	nivel_riesgo = models.CharField(
		max_length=20,
		choices=NIVEL_RIESGO_CHOICES,
		default='bajo'
	)
	alertas_psicologicas = models.TextField(
		blank=True,
		default='Sin alertas'
	)
	requiere_intervencion = models.BooleanField(
		default=False,
		help_text="Indica si se requiere intervención de psicólogo"
	)
	
	# URLs de gráficos
	url_grafico_distribucion = models.URLField(
		blank=True,
		null=True
	)
	url_grafico_radar = models.URLField(
		blank=True,
		null=True
	)
	url_grafico_indicadores = models.URLField(
		blank=True,
		null=True
	)
	
	# Datos JSON completo de Groq
	datos_json = models.JSONField(
		default=dict,
		blank=True,
		help_text="Respuesta completa de Groq"
	)
	
	# Timestamps
	fecha_analisis = models.DateTimeField(
		auto_now_add=True,
		help_text="Fecha/hora cuando se generó el análisis"
	)
	created_at = models.DateTimeField(
		auto_now_add=True
	)
	updated_at = models.DateTimeField(
		auto_now=True
	)
	
	class Meta:
		ordering = ['-fecha_analisis']
		indexes = [
			models.Index(fields=['savefile_id']),
			models.Index(fields=['usuario_id']),
			models.Index(fields=['fecha_analisis']),
		]

	def __str__(self):
		return f"Análisis {self.sesion.escenario_nombre} - {self.usuario.username}"