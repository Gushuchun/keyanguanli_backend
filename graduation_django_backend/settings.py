"""
Django settings for graduation_django_backend project.

Generated by 'django-admin startproject' using Django 5.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# token加密密钥
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', True)

ALLOWED_HOSTS = ['8.138.116.127']

AUTH_USER_MODEL = 'user.UserModel'

# Application definition

INSTALLED_APPS = [
    # "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    'corsheaders',
    'django_extensions',
    'minio_storage',
    "apps.user",
    "apps.team",
    "apps.competition",
    "apps.admin",
    "apps.college",
    "apps.teacher",
    "apps.student",
    "apps.settings",
    "apps.patent",
    "apps.paper"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "utils.middleware.csrf_middleware.NotUseCsrfTokenMiddlewareMixin",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "utils.middleware.token_auth_middleware.TokenAuthMiddleware",  # 添加token验证中间件
]

# 跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CORS_ORIGIN_WHITELIST = [
    "http://*",
    "https://*",
]
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'cache-control',
    'x-token',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,
}

ROOT_URLCONF = "graduation_django_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "graduation_django_backend.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        "NAME": os.getenv('DB_NAME', 'uim_db'),
        "USER": os.getenv('DB_USER', 'root'),
        "PASSWORD": os.getenv('DB_PASSWORD', '123456jl'),
        "HOST": os.getenv('DB_HOST', 'localhost'),
        "PORT": os.getenv('DB_PORT', '3306'),
    }
}

# MINIO配置
MINIO_STORAGE_ENDPOINT = os.getenv('MINIO_STORAGE_ENDPOINT')
MINIO_STORAGE_ACCESS_KEY = os.getenv('MINIO_STORAGE_ACCESS_KEY')
MINIO_STORAGE_SECRET_KEY = os.getenv('MINIO_STORAGE_SECRET_KEY')
MINIO_STORAGE_USE_HTTPS = os.getenv('MINIO_STORAGE_USE_HTTPS', 'False') == 'True'
MINIO_MAX_UPLOAD_SIZE = int(os.getenv('MINIO_MAX_UPLOAD_SIZE', 5 * 1024 * 1024))
MINIO_STORAGE_MEDIA_BUCKET_NAME = os.getenv('MINIO_STORAGE_MEDIA_BUCKET_NAME', 'media')
MINIO_STORAGE_MEDIA_PATENTS = os.getenv('MINIO_STORAGE_MEDIA_PATENTS', 'patents')
MINIO_STORAGE_MEDIA_PAPERS = os.getenv('MINIO_STORAGE_MEDIA_PATENTS', 'papers')
MINIO_STORAGE_MEDIA_COMPETITIONS = os.getenv('MINIO_STORAGE_MEDIA_COMPETITIONS', 'competitions')
MINIO_STORAGE_MEDIA_AVATAR = os.getenv('MINIO_STORAGE_MEDIA_AVATAR', 'avatar')
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = os.getenv('MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET', 'True') == 'True'
MINIO_SECURE = os.getenv('MINIO_SECURE', 'True') == 'True'

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 身份证加密密钥
FERNET_KEY=os.environ.get('FERNET_KEY')

log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

SMS_CODE_EXPIRE = 300  # 验证码过期时间（秒）
SMS_SEND_AGAIN = 60  # 再次发送验证码的间隔时间（秒）

GEOIP_PATH = os.path.join(BASE_DIR, 'utils', 'service', '../resource/GeoLite2-City.mmdb')

# Celery 配置
CELERY_BROKER_URL = f"redis://:{os.getenv('CELERY_BROKER_REDIS_PASSWORD')}@{os.getenv('CELERY_BROKER_REDIS_HOST')}:{os.getenv('CELERY_BROKER_REDIS_PORT')}/{os.getenv('CELERY_BROKER_REDIS_DB')}"
CELERY_RESULT_BACKEND = f"redis://:{os.getenv('CELERY_RESULT_REDIS_PASSWORD')}@{os.getenv('CELERY_RESULT_REDIS_HOST')}:{os.getenv('CELERY_RESULT_REDIS_PORT')}/{os.getenv('CELERY_RESULT_REDIS_DB')}"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{os.getenv('CACHE_REDIS_PASSWORD')}@{os.getenv('CACHE_REDIS_HOST')}:{os.getenv('CACHE_REDIS_PORT')}/{os.getenv('CACHE_REDIS_DB')}",  # Redis 服务器地址和数据库编号
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # "PASSWORD": "123456jl",  # 如果有密码需要配置
        },
        "KEY_PREFIX": "myproject"  # 缓存键前缀
    }
}

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_user': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'user.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_team': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'team.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_competition': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'competition.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_admin': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'admin.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_college': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'college.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_teacher': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'teacher.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_student': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'student.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_all': {
            'level': 'DEBUG',  # 记录所有日志（DEBUG 及以上级别）
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'all.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_error': {
            'level': 'DEBUG',  # 只记录 ERROR 及以上级别
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'error.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'delay': True,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'filters': {
        'no_warnings': {
            '()': 'logging.Filter',
            'name': 'warning',
        },
    },
    'loggers': {
        'user': {
            'handlers': ['file_user', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'team': {
            'handlers': ['file_team', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'competition': {
            'handlers': ['file_competition', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'admin': {
            'handlers': ['file_admin', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'college': {
            'handlers': ['file_college', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'teacher': {
            'handlers': ['file_teacher', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'student': {
            'handlers': ['file_student', 'file_all', 'file_error' ,'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['file_security', 'file_all', 'file_error', 'console'],
            'level': 'WARNING',  # 只关注警告及以上级别（可根据需要改为 INFO）
            'propagate': False,
        },
        # 捕获所有未指定的日志
        '': {
            'handlers': ['file_all', 'file_error' ,'console'],
            'level': 'ERROR',
            'propagate': False,
        },
        # 避免捕获到 all.log
        'django.utils.autoreload': {
            'handlers': [],
            'propagate': False,
        },
        # 'django.request': {
        #     'handlers': ['file_error'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        # 'django.server': {
        #     'handlers': ['file_error'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
    },
}