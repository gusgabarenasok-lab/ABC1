"""
Django settings for SIPROSA MES Backend
Configuración unificada para desarrollo y producción
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ============================================
# BASE CONFIGURATION
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Detectar entorno
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# Cargar variables de entorno según el ambiente
if IS_PRODUCTION:
    env_path = BASE_DIR / ".env.prod"
else:
    env_path = BASE_DIR / ".env.dev"

load_dotenv(env_path)
print(f"📦 Entorno: {ENVIRONMENT}")
print(f"📂 Archivo .env: {env_path}")

# ============================================
# SECURITY SETTINGS
# ============================================
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("❌ SECRET_KEY no está configurada en las variables de entorno")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# ============================================
# APPLICATION DEFINITION
# ============================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'core',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise debe ir después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'backend.middleware.error_handler.GlobalErrorMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'

# ============================================
# DATABASE
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# ============================================
# PASSWORD VALIDATION
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================================
# INTERNATIONALIZATION
# ============================================
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# ============================================
# STATIC FILES
# ============================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration para servir archivos estáticos en producción
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ============================================
# DEFAULT PRIMARY KEY
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# CORS & CSRF CONFIGURATION
# ============================================
CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") 
    if origin.strip()
]

CSRF_TRUSTED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") 
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

# ============================================
# SECURITY HEADERS (Base)
# ============================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# ============================================
# PRODUCTION SECURITY SETTINGS
# ============================================
if IS_PRODUCTION:
    # HTTPS y cookies seguras
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    
    # HSTS (HTTP Strict Transport Security)
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    print("🔒 Configuración de seguridad para PRODUCCIÓN activada")
else:
    # Desarrollo: cookies sin HTTPS
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    
    print("🔓 Configuración de seguridad para DESARROLLO")

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} - {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 3,
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file"],
            "level": "DEBUG" if DEBUG else "INFO",
            "propagate": False,
        },
    },
}

# ============================================
# DJANGO REST FRAMEWORK
# ============================================
REST_FRAMEWORK = {
    # Autenticación
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    
    # Permisos
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    
    # Paginación
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    
    # Filtrado y búsqueda
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    
    # Throttling (limitación de peticiones)
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
    
    # Formato de respuesta
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
}

# ============================================
# SIMPLE JWT CONFIGURATION
# ============================================
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),  # Token válido por 8 horas (jornada laboral)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

print("✅ Configuración cargada correctamente")
