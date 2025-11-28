from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
	SesionSimulacion,
	ProgresoHistorico,
	DecisionTomada,
	EventoOcurrido,
	MetricaDesempeno,
	SaveFileUsuario,
	AnalisisIA
)
from .serializers import (
	SesionSimulacionDetailSerializer,
	SesionSimulacionListSerializer,
	SesionSimulacionCreateSerializer,
	ProgresoHistoricoSerializer,
	DecisionTomadaSerializer,
	EventoOcurridoSerializer,
	MetricaDesempenoSerializer,
	SaveFileUsuarioSerializer,
	UserSerializer,
	UserRegistrationSerializer,
	UserDetailSerializer,
	ChangePasswordSerializer,
	AnalisisIAListSerializer,
	AnalisisIADetailSerializer,
	AnalisisIACreateSerializer,
)


# ============================================
# AUTENTICACIÓN CUSTOMIZADA - LOGIN CON EMAIL
# ============================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
	"""
	Serializer customizado que acepta email O username
	Busca el usuario por email y luego valida la contraseña
	"""
	username_field = 'email'
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if 'username' in self.fields:
			self.fields['email'] = self.fields.pop('username')
	
	def validate(self, attrs):
		"""Validar credenciales usando email"""
		email = attrs.get('email')
		password = attrs.get('password')
		
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			raise serializers.ValidationError({'email': 'No existe un usuario con este email'})

		if not user.check_password(password):
			raise serializers.ValidationError({'password': 'Contraseña incorrecta'})

		if not user.is_active:
			raise serializers.ValidationError({'error': 'Usuario desactivado'})
		
		refresh = self.get_token(user)
		
		data = {
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
		
		return data


class CustomTokenObtainPairView(TokenObtainPairView):
	"""Vista customizada para obtener tokens usando email"""
	serializer_class = CustomTokenObtainPairSerializer
	permission_classes = [AllowAny]


# ============================================
# SESIONES
# ============================================

class SesionSimulacionViewSet(viewsets.ModelViewSet):
	"""ViewSet para gestionar sesiones de simulación"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = SesionSimulacion.objects.all()

	def get_serializer_class(self):
		if self.action == 'create':
			return SesionSimulacionCreateSerializer
		elif self.action == 'retrieve':
			return SesionSimulacionDetailSerializer
		return SesionSimulacionListSerializer

	def get_queryset(self):
		"""Solo sesiones del usuario autenticado"""
		return SesionSimulacion.objects.filter(
			usuario=self.request.user
		).select_related('usuario').prefetch_related('decisiones', 'eventos')

	def perform_create(self, serializer):
		serializer.save(usuario=self.request.user)

	@action(detail=False, methods=['get'])
	def mi_historial(self, request):
		"""Obtiene historial de sesiones del usuario"""
		sesiones = self.get_queryset().order_by('-fecha_inicio')
		page = self.paginate_queryset(sesiones)

		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(sesiones, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['post'])
	def completar(self, request, pk=None):
		"""Marca sesión como completada"""
		sesion = self.get_object()

		if sesion.usuario != request.user:
			return Response(
				{'error': 'No tienes permisos para modificar esta sesión'},
				status=status.HTTP_403_FORBIDDEN
			)

		sesion.completada = True
		sesion.fecha_fin = timezone.now()

		if sesion.fecha_inicio:
			duracion = sesion.fecha_fin - sesion.fecha_inicio
			sesion.duracion_segundos = int(duracion.total_seconds())

		sesion.save()

		serializer = self.get_serializer(sesion)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def datos_para_n8n(self, request, pk=None):
		"""Retorna datos para procesamiento en N8N"""
		sesion = self.get_object()

		decisiones = list(DecisionTomada.objects.filter(sesion=sesion).values())
		eventos = list(EventoOcurrido.objects.filter(sesion=sesion).values())
		metricas = getattr(sesion, 'metricas', None)

		datos = {
			'sesion': {
				'id': sesion.id,
				'usuario_id': sesion.usuario.id,
				'escenario': sesion.escenario_nombre,
				'fecha_inicio': sesion.fecha_inicio.isoformat() if sesion.fecha_inicio else None,
				'fecha_fin': sesion.fecha_fin.isoformat() if sesion.fecha_fin else None,
				'duracion_segundos': sesion.duracion_segundos,
				'completada': sesion.completada,
			},
			'decisiones': decisiones,
			'eventos': eventos,
			'metricas_existentes': {
				'id': metricas.id if metricas else None,
				'nivel_estres': metricas.nivel_estres if metricas else None,
			} if metricas else None
		}

		return Response(datos)


class DecisionTomadaViewSet(viewsets.ModelViewSet):
	"""ViewSet para decisiones"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = DecisionTomadaSerializer

	def get_queryset(self):
		"""Solo decisiones de sesiones del usuario"""
		return DecisionTomada.objects.filter(
			sesion__usuario=self.request.user
		).select_related('sesion')

	def perform_create(self, serializer):
		sesion_id = self.request.data.get('sesion')
		try:
			sesion = SesionSimulacion.objects.get(
				id=sesion_id,
				usuario=self.request.user
			)
			serializer.save(sesion=sesion)
		except SesionSimulacion.DoesNotExist:
			return Response(
				{'error': 'Sesión no encontrada'},
				status=status.HTTP_404_NOT_FOUND
			)

	@action(detail=False, methods=['get'])
	def por_sesion(self, request):
		"""Obtiene decisiones de una sesión específica"""
		sesion_id = request.query_params.get('sesion_id')

		if not sesion_id:
			return Response(
				{'error': 'Parámetro sesion_id requerido'},
				status=status.HTTP_400_BAD_REQUEST
			)

		decisiones = self.get_queryset().filter(sesion_id=sesion_id)
		serializer = self.get_serializer(decisiones, many=True)
		return Response(serializer.data)


class EventoOcurridoViewSet(viewsets.ModelViewSet):
	"""ViewSet para eventos"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = EventoOcurridoSerializer

	def get_queryset(self):
		"""Solo eventos de sesiones del usuario"""
		return EventoOcurrido.objects.filter(
			sesion__usuario=self.request.user
		).select_related('sesion')

	def perform_create(self, serializer):
		sesion_id = self.request.data.get('sesion')
		try:
			sesion = SesionSimulacion.objects.get(
				id=sesion_id,
				usuario=self.request.user
			)
			serializer.save(sesion=sesion)
		except SesionSimulacion.DoesNotExist:
			return Response(
				{'error': 'Sesión no encontrada'},
				status=status.HTTP_404_NOT_FOUND
			)


class MetricaDesempenoViewSet(viewsets.ReadOnlyModelViewSet):
	"""ViewSet de solo lectura para métricas"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = MetricaDesempenoSerializer

	def get_queryset(self):
		"""Solo métricas de sesiones del usuario"""
		return MetricaDesempeno.objects.filter(
			sesion__usuario=self.request.user
		).select_related('sesion')


class ProgresoHistoricoViewSet(viewsets.ReadOnlyModelViewSet):
	"""ViewSet para progreso histórico"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = ProgresoHistoricoSerializer

	def get_queryset(self):
		"""Solo progreso del usuario autenticado"""
		return ProgresoHistorico.objects.filter(
			usuario=self.request.user
		).order_by('-fecha_calculo')


class SaveFileUsuarioViewSet(viewsets.ModelViewSet):
	"""ViewSet para archivos guardados"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	serializer_class = SaveFileUsuarioSerializer

	def get_queryset(self):
		"""Solo savefiles del usuario autenticado"""
		return SaveFileUsuario.objects.filter(
			usuario=self.request.user
		).order_by('-ultima_actualizacion')

	def perform_create(self, serializer):
		serializer.save(usuario=self.request.user)

	@action(detail=False, methods=['get'])
	def ultimo(self, request):
		"""Obtiene el último savefile del usuario"""
		savefile = self.get_queryset().first()

		if not savefile:
			return Response(
				{'error': 'No tienes savefiles registrados'},
				status=status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(savefile)
		return Response(serializer.data)


# ============================================
# ANÁLISIS IA - VIEWSET ACTUALIZADO
# ============================================

class AnalisisIAViewSet(viewsets.ModelViewSet):
	"""ViewSet para análisis IA generados por Groq"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]
	queryset = AnalisisIA.objects.all()

	def get_serializer_class(self):
		if self.action == 'create':
			return AnalisisIACreateSerializer
		elif self.action == 'retrieve':
			return AnalisisIADetailSerializer
		return AnalisisIAListSerializer

	def get_queryset(self):
		"""
		Usuarios normales ven solo sus análisis.
		Admins ven todos.
		"""
		if self.request.user.is_staff or self.request.user.is_superuser:
			return AnalisisIA.objects.all().order_by('-timestamp_analisis')
		return AnalisisIA.objects.filter(
			usuario=self.request.user
		).order_by('-timestamp_analisis')

	def perform_create(self, serializer):
		"""N8N guarda el análisis"""
		serializer.save()

	@action(detail=False, methods=['get'])
	def mis_analisis(self, request):
		"""Análisis del usuario autenticado"""
		analisis = AnalisisIA.objects.filter(
			usuario=request.user
		).order_by('-timestamp_analisis')
		
		page = self.paginate_queryset(analisis)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		
		serializer = self.get_serializer(analisis, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
	def todos(self, request):
		"""
		SOLO PARA ADMINS: Ver todos los análisis
		GET /api/v1/dashboard/analisis-ia/todos/
		"""
		if not (request.user.is_staff or request.user.is_superuser):
			return Response(
				{'error': 'No tienes permisos para ver todos los análisis'},
				status=status.HTTP_403_FORBIDDEN
			)
		
		analisis = AnalisisIA.objects.all().order_by('-timestamp_analisis')
		
		page = self.paginate_queryset(analisis)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		
		serializer = self.get_serializer(analisis, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def por_savefile(self, request):
		"""Obtiene análisis de un savefile específico"""
		savefile_id = request.query_params.get('savefile_id')

		if not savefile_id:
			return Response(
				{'error': 'Parámetro savefile_id requerido'},
				status=status.HTTP_400_BAD_REQUEST
			)

		if request.user.is_staff or request.user.is_superuser:
			analisis = AnalisisIA.objects.filter(savefile_id=savefile_id).first()
		else:
			analisis = self.get_queryset().filter(savefile_id=savefile_id).first()
			
		if not analisis:
			return Response(
				{'error': 'Análisis no encontrado'},
				status=status.HTTP_404_NOT_FOUND
			)

		serializer = self.get_serializer(analisis)
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def ultimos(self, request):
		"""Obtiene los últimos 10 análisis del usuario"""
		analisis = self.get_queryset()[:10]
		serializer = self.get_serializer(analisis, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def por_riesgo(self, request):
		"""Obtiene análisis filtrados por nivel de riesgo"""
		nivel_riesgo = request.query_params.get('nivel', 'alto')
		
		if request.user.is_staff or request.user.is_superuser:
			analisis = AnalisisIA.objects.filter(nivel_riesgo=nivel_riesgo)
		else:
			analisis = self.get_queryset().filter(nivel_riesgo=nivel_riesgo)
		
		serializer = self.get_serializer(analisis, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def requieren_intervencion(self, request):
		"""Obtiene análisis que requieren intervención"""
		if not (request.user.is_staff or request.user.is_superuser):
			return Response(
				{'error': 'Solo admins pueden ver esto'},
				status=status.HTTP_403_FORBIDDEN
			)
		
		analisis = AnalisisIA.objects.filter(
			requiere_intervencion=True
		).order_by('-timestamp_analisis')
		
		serializer = self.get_serializer(analisis, many=True)
		return Response(serializer.data)

	@action(detail=False, methods=['get'])
	def estadisticas(self, request):
		"""Estadísticas de análisis (solo para admins)"""
		if not (request.user.is_staff or request.user.is_superuser):
			return Response(
				{'error': 'Solo admins pueden ver esto'},
				status=status.HTTP_403_FORBIDDEN
			)
		
		total = AnalisisIA.objects.count()
		por_riesgo = {
			'bajo': AnalisisIA.objects.filter(nivel_riesgo='bajo').count(),
			'leve': AnalisisIA.objects.filter(nivel_riesgo='leve').count(),
			'moderado': AnalisisIA.objects.filter(nivel_riesgo='moderado').count(),
			'alto': AnalisisIA.objects.filter(nivel_riesgo='alto').count(),
			'severo': AnalisisIA.objects.filter(nivel_riesgo='severo').count(),
		}
		requieren_intervencion = AnalisisIA.objects.filter(
			requiere_intervencion=True
		).count()
		
		return Response({
			'total_analisis': total,
			'por_riesgo': por_riesgo,
			'requieren_intervencion': requieren_intervencion,
		})
	
# ============================================
# AUTENTICACIÓN Y USUARIO
# ============================================

class RegisterViewSet(viewsets.ViewSet):
	"""ViewSet para registro de nuevos usuarios"""
	permission_classes = [AllowAny]

	def create(self, request):
		"""Registrar un nuevo usuario - POST /auth/register/"""
		serializer = UserRegistrationSerializer(data=request.data)

		if serializer.is_valid():
			user = serializer.save()
			return Response({
				'id': user.id,
				'username': user.username,
				'email': user.email,
				'first_name': user.first_name,
				'last_name': user.last_name,
				'message': 'Usuario registrado exitosamente'
			}, status=status.HTTP_201_CREATED)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def list(self, request):
		"""GET /auth/register/ - No permitido"""
		return Response(
			{'error': 'Método GET no permitido en registro'},
			status=status.HTTP_405_METHOD_NOT_ALLOWED
		)


class UserProfileViewSet(viewsets.ViewSet):
	"""ViewSet para gestión de perfil de usuario autenticado"""
	authentication_classes = [JWTAuthentication]
	permission_classes = [IsAuthenticated]

	@action(detail=False, methods=['get'])
	def me(self, request):
		"""Obtener datos del usuario autenticado"""
		serializer = UserDetailSerializer(request.user)
		return Response(serializer.data)

	@action(detail=False, methods=['patch'])
	def update_profile(self, request):
		"""Actualizar perfil del usuario"""
		user = request.user

		if 'first_name' in request.data:
			user.first_name = request.data['first_name']

		if 'last_name' in request.data:
			user.last_name = request.data['last_name']

		if 'email' in request.data:
			email = request.data['email'].strip()
			if User.objects.filter(email=email).exclude(id=user.id).exists():
				return Response(
					{'error': 'Este email ya está registrado'},
					status=status.HTTP_400_BAD_REQUEST
				)
			user.email = email

		user.save()
		serializer = UserDetailSerializer(user)
		return Response(serializer.data)

	@action(detail=False, methods=['post'])
	def change_password(self, request):
		"""Cambiar contraseña del usuario"""
		user = request.user
		serializer = ChangePasswordSerializer(data=request.data)

		if serializer.is_valid():
			# Validar contraseña actual
			if not user.check_password(serializer.validated_data['old_password']):
				return Response(
					{'error': 'La contraseña actual es incorrecta'},
					status=status.HTTP_400_BAD_REQUEST
				)

			# Establecer nueva contraseña
			user.set_password(serializer.validated_data['new_password'])
			user.save()

			return Response({
				'message': 'Contraseña cambiada exitosamente'
			}, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)