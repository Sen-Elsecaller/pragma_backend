from django.contrib import admin
from .models import (
	SesionSimulacion,
	ProgresoHistorico,
	DecisionTomada,
	EventoOcurrido,
	MetricaDesempeno,
	SaveFileUsuario
)


@admin.register(SesionSimulacion)
class SesionSimulacionAdmin(admin.ModelAdmin):
	list_display = ('id', 'usuario', 'escenario_nombre', 'fecha_inicio', 'completada')
	list_filter = ('completada', 'fecha_inicio')
	search_fields = ('usuario__username', 'escenario_nombre')
	readonly_fields = ('created_at', 'updated_at', 'fecha_inicio')
	fieldsets = (
		('Información General', {
			'fields': ('usuario', 'escenario_nombre')
		}),
		('Duración', {
			'fields': ('fecha_inicio', 'fecha_fin', 'duracion_segundos')
		}),
		('Estado', {
			'fields': ('completada',)
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)


@admin.register(ProgresoHistorico)
class ProgresoHistoricoAdmin(admin.ModelAdmin):
	list_display = ('id', 'usuario', 'fecha_calculo', 'promedio_estres', 'sesiones_completadas')
	list_filter = ('fecha_calculo',)
	search_fields = ('usuario__username',)
	readonly_fields = ('created_at', 'fecha_calculo')
	fieldsets = (
		('Usuario', {
			'fields': ('usuario',)
		}),
		('Métricas', {
			'fields': (
				'promedio_estres',
				'sesiones_completadas',
				'tiempo_total_minutos',
				'escenarios_practicados'
			)
		}),
		('Información', {
			'fields': ('fecha_calculo', 'created_at'),
			'classes': ('collapse',)
		}),
	)


@admin.register(DecisionTomada)
class DecisionTomadaAdmin(admin.ModelAdmin):
	list_display = ('id', 'sesion', 'decision_id', 'fue_acertada', 'timestamp_decision')
	list_filter = ('fue_acertada', 'timestamp_decision')
	search_fields = ('sesion__escenario_nombre', 'decision_id')
	readonly_fields = ('created_at', 'timestamp_decision')
	fieldsets = (
		('Sesión', {
			'fields': ('sesion',)
		}),
		('Decisión', {
			'fields': ('decision_id', 'tiempo_respuesta_segundos', 'fue_acertada')
		}),
		('Información', {
			'fields': ('timestamp_decision', 'created_at'),
			'classes': ('collapse',)
		}),
	)


@admin.register(EventoOcurrido)
class EventoOcurridoAdmin(admin.ModelAdmin):
	list_display = ('id', 'sesion', 'evento_id', 'fue_manejado_correctamente', 'timestamp_ocurrencia')
	list_filter = ('fue_manejado_correctamente', 'timestamp_ocurrencia')
	search_fields = ('sesion__escenario_nombre', 'evento_id')
	readonly_fields = ('created_at',)
	fieldsets = (
		('Sesión', {
			'fields': ('sesion',)
		}),
		('Evento', {
			'fields': ('evento_id', 'timestamp_ocurrencia', 'fue_manejado_correctamente')
		}),
		('Información', {
			'fields': ('created_at',),
			'classes': ('collapse',)
		}),
	)


@admin.register(MetricaDesempeno)
class MetricaDesempenoAdmin(admin.ModelAdmin):
	list_display = ('id', 'sesion', 'nivel_estres', 'porcentaje_acierto', 'eventos_manejados')
	list_filter = ('nivel_estres', 'timestamp_captura')
	search_fields = ('sesion__escenario_nombre',)
	readonly_fields = ('created_at', 'timestamp_captura', 'porcentaje_acierto')
	fieldsets = (
		('Sesión', {
			'fields': ('sesion',)
		}),
		('Desempeño', {
			'fields': (
				'nivel_estres',
				'decisiones_acertadas',
				'decisiones_totales',
				'porcentaje_acierto',
				'tiempo_promedio_decision',
				'eventos_manejados'
			)
		}),
		('Información', {
			'fields': ('timestamp_captura', 'created_at'),
			'classes': ('collapse',)
		}),
	)


@admin.register(SaveFileUsuario)
class SaveFileUsuarioAdmin(admin.ModelAdmin):
	list_display = ('id', 'usuario', 'version_savefile', 'ultima_actualizacion')
	list_filter = ('version_savefile', 'ultima_actualizacion')
	search_fields = ('usuario__username',)
	readonly_fields = ('created_at', 'ultima_actualizacion')
	fieldsets = (
		('Usuario', {
			'fields': ('usuario',)
		}),
		('Archivo', {
			'fields': ('datos_savefile', 'version_savefile')
		}),
		('Información', {
			'fields': ('ultima_actualizacion', 'created_at'),
			'classes': ('collapse',)
		}),
	)