from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
	CustomTokenObtainPairView,
	SesionSimulacionViewSet,
	DecisionTomadaViewSet,
	EventoOcurridoViewSet,
	MetricaDesempenoViewSet,
	ProgresoHistoricoViewSet,
	SaveFileUsuarioViewSet,
	RegisterViewSet,
	UserProfileViewSet,
	AnalisisIAViewSet,
)

app_name = 'pragma_dashboard'

router = DefaultRouter()
router.register(r'sesiones', SesionSimulacionViewSet, basename='sesion')
router.register(r'decisiones', DecisionTomadaViewSet, basename='decision')
router.register(r'eventos', EventoOcurridoViewSet, basename='evento')
router.register(r'metricas', MetricaDesempenoViewSet, basename='metrica')
router.register(r'progreso', ProgresoHistoricoViewSet, basename='progreso')
router.register(r'savefiles', SaveFileUsuarioViewSet, basename='savefile')
router.register(r'analisis-ia', AnalisisIAViewSet, basename='analisis-ia')
router.register(r'auth/register', RegisterViewSet, basename='register')
router.register(r'auth/profile', UserProfileViewSet, basename='profile')

urlpatterns = [
	# Login customizado con email (sin token en root)
	path('auth/login/', CustomTokenObtainPairView.as_view(), name='auth_login'),
	
	# Rutas de router
	path('', include(router.urls)),
]