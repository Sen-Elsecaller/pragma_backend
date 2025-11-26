"""
Django settings for PRAGMA Backend project - VERSIÓN ACTUALIZADA PARA DASHBOARD.

Configuración completa y lista para producción con autenticación JWT sólida.
"""

import os
import dj_database_url
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# SECURITY SETTINGS
# ============================================

SECRET_KEY = os.environ.get(
	'SECRET_KEY',
	'django-insecure-gxd*rmig8aqsu!nm(^sizj!#rty9b9(3!z40j)r%z7)9my(kak'
)

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,98.87.220.175').split(',')


CSRF_TRUSTED_ORIGINS = os.environ.get(
	'CSRF_TRUSTED_ORIGINS',
	'http://localhost:3000,http://localhost:5173'
).split(',')

CORS_ALLOWED_ORIGINS = os.environ.get(
	'CORS_ALLOWED_ORIGINS', 
	'http://localhost:3000,http://localhost:5173'
).split(',')

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_HEADERS = [
	'accept',
	'accept-encoding',
	'authorization',
	'content-type',
	'dnt',
	'origin',
	'user-agent',
	'x-csrftoken',
	'x-requested-with',
]

# ============================================
# APPLICATION DEFINITION
# ============================================

INSTALLED_APPS = [
	# Django Core Apps
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	
	# Third Party Apps - ORDEN IMPORTANTE
	'rest_framework',
	'rest_framework_simplejwt',
	'corsheaders',
	'django_filters',
	'drf_yasg',
	
	# Local Apps
	'apps.pragma_dashboard', 
]

MIDDLEWARE = [
	'django.middleware.security.SecurityMiddleware',
	'whitenoise.middleware.WhiteNoiseMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [BASE_DIR / 'templates'],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
			],
		},
	},
]

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================
# DATABASE CONFIGURATION
# ============================================

if os.environ.get('DATABASE_URL'):
	DATABASES = {
		'default': dj_database_url.config(
			default=os.environ.get('DATABASE_URL'),
			conn_max_age=600,
			conn_health_checks=True,
			ssl_require=True,
		)
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql',
			'NAME': os.environ.get('DB_NAME', 'railway'),
			'USER': os.environ.get('DB_USER', 'postgres'),
			'PASSWORD': os.environ.get('DB_PASSWORD', 'BkurrjOpNTnepNQAvfQqLANJGiITphwC'),
			'HOST': os.environ.get('DB_HOST', 'centerbeam.proxy.rlwy.net'),
			'PORT': os.environ.get('DB_PORT', '47459'),
			'CONN_MAX_AGE': 600,
			'OPTIONS': {
				'sslmode': 'disable',
			},
		}
	}


# ============================================
# PASSWORD VALIDATION
# ============================================

AUTH_PASSWORD_VALIDATORS = [
	{
		'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
		'OPTIONS': {
			'min_length': 8,
		}
	},
	{
		'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
	},
	{
		'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
	},
]

# ============================================
# INTERNATIONALIZATION
# ============================================

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i:s'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# ============================================
# STATIC FILES
# ============================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================
# MEDIA FILES
# ============================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ============================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# REST FRAMEWORK CONFIGURATION
# ============================================

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': [
		'rest_framework_simplejwt.authentication.JWTAuthentication',
		'rest_framework.authentication.SessionAuthentication',
	],
	
	'DEFAULT_PERMISSION_CLASSES': [
		'rest_framework.permissions.IsAuthenticatedOrReadOnly',
	],
	
	'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
	'PAGE_SIZE': 50,
	
	'DEFAULT_FILTER_BACKENDS': [
		'django_filters.rest_framework.DjangoFilterBackend',
		'rest_framework.filters.SearchFilter',
		'rest_framework.filters.OrderingFilter',
	],
	
	'DEFAULT_RENDERER_CLASSES': [
		'rest_framework.renderers.JSONRenderer',
	] + (['rest_framework.renderers.BrowsableAPIRenderer'] if DEBUG else []),
	
	'DEFAULT_PARSER_CLASSES': [
		'rest_framework.parsers.JSONParser',
		'rest_framework.parsers.FormParser',
		'rest_framework.parsers.MultiPartParser',
	],
	
	'DEFAULT_THROTTLE_CLASSES': [
		'rest_framework.throttling.AnonRateThrottle',
		'rest_framework.throttling.UserRateThrottle',
	],
	'DEFAULT_THROTTLE_RATES': {
		'anon': '100/hour',
		'user': '1000/hour',
	},
	
	'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
	
	'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
	'DATE_FORMAT': '%Y-%m-%d',
	'TIME_FORMAT': '%H:%M:%S',
	
	'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# ============================================
# JWT CONFIGURATION (Simple JWT)
# ============================================

SIMPLE_JWT = {
	'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
	'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
	
	'ROTATE_REFRESH_TOKENS': True,
	'BLACKLIST_AFTER_ROTATION': True,
	'UPDATE_LAST_LOGIN': True,
	
	'ALGORITHM': 'HS256',
	'SIGNING_KEY': SECRET_KEY,
	'VERIFYING_KEY': None,
	'AUDIENCE': None,
	'ISSUER': None,
	'JWK_URL': None,
	'LEEWAY': 0,
	
	'AUTH_HEADER_TYPES': ('Bearer',),
	'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
	
	'USER_ID_FIELD': 'id',
	'USER_ID_CLAIM': 'user_id',
	'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
	
	'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
	'TOKEN_TYPE_CLAIM': 'token_type',
	'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
	
	'JTI_CLAIM': 'jti',
	'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
	'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
	'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ============================================
# SWAGGER/OPENAPI DOCUMENTATION
# ============================================

SWAGGER_SETTINGS = {
	'SECURITY_DEFINITIONS': {
		'Bearer': {
			'type': 'apiKey',
			'name': 'Authorization',
			'in': 'header',
			'description': 'JWT Token. Ejemplo: "Bearer {token}"'
		}
	},
	'USE_SESSION_AUTH': False,
	'JSON_EDITOR': True,
	'SUPPORTED_SUBMIT_METHODS': ['get', 'post', 'put', 'patch', 'delete'],
	'DEFAULT_MODEL_RENDERING': 'example',
	'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_yasg.inspectors.SwaggerAutoSchema',
}

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '[{levelname}] {asctime} {name} {module} {process:d} {thread:d} - {message}',
			'style': '{',
		},
		'simple': {
			'format': '[{levelname}] {asctime} - {message}',
			'style': '{',
		},
	},
	'filters': {
		'require_debug_true': {
			'()': 'django.utils.log.RequireDebugTrue',
		},
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse',
		},
	},
	'handlers': {
		'console': {
			'level': 'INFO',
			'class': 'logging.StreamHandler',
			'formatter': 'simple'
		},
		'file': {
			'level': 'ERROR',
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': BASE_DIR / 'logs' / 'django_errors.log',
			'maxBytes': 1024 * 1024 * 10,
			'backupCount': 5,
			'formatter': 'verbose',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console', 'file'],
			'level': 'INFO',
			'propagate': False,
		},
		'django.request': {
			'handlers': ['console', 'file'],
			'level': 'ERROR',
			'propagate': False,
		},
		'apps': {
			'handlers': ['console', 'file'],
			'level': 'DEBUG' if DEBUG else 'INFO',
			'propagate': False,
		},
	},
	'root': {
		'handlers': ['console'],
		'level': 'INFO',
	},
}

(BASE_DIR / 'logs').mkdir(exist_ok=True)

# ============================================
# CUSTOM SETTINGS - PRAGMA SPECIFIC
# ============================================

FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', '')

# ============================================
# PRODUCTION SECURITY SETTINGS
# ============================================

if not DEBUG:
	SECURE_SSL_REDIRECT = False
	
	SESSION_COOKIE_SECURE = True
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SAMESITE = 'Lax'
	
	CSRF_COOKIE_SECURE = True
	CSRF_COOKIE_HTTPONLY = True
	CSRF_COOKIE_SAMESITE = 'Lax'
	
	SECURE_BROWSER_XSS_FILTER = True
	SECURE_CONTENT_TYPE_NOSNIFF = True
	X_FRAME_OPTIONS = 'DENY'
	
	SECURE_HSTS_SECONDS = 0
	SECURE_HSTS_INCLUDE_SUBDOMAINS =False
	SECURE_HSTS_PRELOAD = False
	
	SECURE_REFERRER_POLICY = 'same-origin'

# ============================================
# CACHE CONFIGURATION
# ============================================

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': 'pragma-cache',
		'TIMEOUT': 300,
		'OPTIONS': {
			'MAX_ENTRIES': 1000
		}
	}
}

# ============================================
# SESSION CONFIGURATION
# ============================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ============================================
# FILE UPLOAD SETTINGS
# ============================================

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880
FILE_UPLOAD_PERMISSIONS = 0o644

# ============================================
# ADMIN CUSTOMIZATION
# ============================================

ADMIN_SITE_HEADER = "PRAGMA Backend Administration"
ADMIN_SITE_TITLE = "PRAGMA Admin"
ADMIN_INDEX_TITLE = "Bienvenido al Panel de Administración"


# ============================================
# INFORMACIÓN DE CONFIGURACIÓN
# ============================================

if DEBUG:
	print("\n" + "="*60)
	print("🚀 PRAGMA Backend - Configuración Cargada")
	print("="*60)
	print(f"DEBUG: {DEBUG}")
	print(f"DATABASE: {DATABASES['default']['ENGINE']}")
	print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
	print(f"CORS_ALLOWED_ORIGINS: {len(CORS_ALLOWED_ORIGINS)} origin(s)")
	print(f"INSTALLED_APPS: {len(INSTALLED_APPS)} apps")
	print(f"MIDDLEWARE: {len(MIDDLEWARE)} middleware(s)")
	print("="*60 + "\n")