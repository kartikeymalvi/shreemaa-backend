# from pathlib import Path
# from datetime import timedelta
# import os

# # Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent

# # SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-!kg0#bb=%*6_h61(3r%3zew*li@&zonaau^64+t)!b^+)7@xvk'

# # 🔥 UPDATE 1: Local testing aur debugging ke liye isey True karna ZAROORI hai!
# DEBUG = True

# # Allowed hosts mein sab allow kar diya local ke liye
# ALLOWED_HOSTS = ['*']

# # Application definition
# INSTALLED_APPS = [
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     'rest_framework',
#     'corsheaders',
#     'rest_framework_simplejwt',
#     'accounts',
#     'order_reports',
# ]

# # Custom User Model define karna zaroori hai
# AUTH_USER_MODEL = 'accounts.CustomUser'

# # Data wahi AWS RDS wala hi use kar rahe hain taaki apka test data na ude
# # SQLite Database (Local Development)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# MIDDLEWARE = [
#     'corsheaders.middleware.CorsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
# ]

# ROOT_URLCONF = 'project.urls'

# # 🔥 UPDATE 2: CORS and CSRF Settings optimized for local
# CORS_ALLOW_ALL_ORIGINS = False  
# CORS_ALLOW_CREDENTIALS = True  

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",  
#     "http://localhost:5173",  
#     "http://127.0.0.1:5500", 
#     "http://127.0.0.1:5173",
#     "https://smg-erp.duckdns.org",
#     "https://shreemaa-frontend.vercel.app",
# ]

# CSRF_TRUSTED_ORIGINS = [
#     "http://localhost:5173",       # <-- Ye line Local testing ke liye add ki hai
#     "http://127.0.0.1:5173",       # <-- Ye bhi add ki hai
#     "https://smg-erp.duckdns.org",
#     "https://shreemaa-frontend.vercel.app",
# ]

# CORS_ALLOW_METHODS = [
#     'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
# ]

# CORS_ALLOW_HEADERS = [
#     'accept', 'accept-encoding', 'authorization', 'content-type', 'dnt',
#     'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
# ]

# # DRF & JWT Settings
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
#     )
# }

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
#     'AUTH_HEADER_TYPES': ('Bearer',),
# }

# TEMPLATES = [
#     {
#         'BACKEND': 'django.template.backends.django.DjangoTemplates',
#         'DIRS': [],
#         'APP_DIRS': True,
#         'OPTIONS': {
#             'context_processors': [
#                 'django.template.context_processors.request',
#                 'django.contrib.auth.context_processors.auth',
#                 'django.contrib.messages.context_processors.messages',
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = 'project.wsgi.application'

# AUTH_PASSWORD_VALIDATORS = [
#     { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
#     { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
#     { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
#     { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
# ]

# LANGUAGE_CODE = 'en-us'
# TIME_ZONE = 'Asia/Kolkata'
# USE_I18N = True
# USE_TZ = True

# STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles'
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# -------------------LIVE SETUP AWS ------------------------------------

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!kg0#bb=%*6_h61(3r%3zew*li@&zonaau^64+t)!b^+)7@xvk'

# SECURITY WARNING: don't run with debug turned on in production!
# Abhi test karne ke liye True rakha hai, baad me live hone ke baad False kar denge
DEBUG = False

# 🔥 UPDATE 1: Render aur Vercel ko allow karne ke liye '*' lagaya hai
ALLOWED_HOSTS = ['43.204.228.19', 'smg-erp.duckdns.org', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',
    'accounts',
    'order_reports',
]

# Custom User Model define karna zaroori hai
AUTH_USER_MODEL = 'accounts.CustomUser'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shreemaa_live_db',
        'USER': 'postgres',
        'PASSWORD': 'Kartikey9406932629',
        'HOST': 'database-1.c5ci8uc0ye03.ap-south-1.rds.amazonaws.com',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}


# 🔥 UPDATE 3: Middleware Sequence Theek Kiya Hai (WhiteNoise hamesha Security ke baad)
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', # CORS hamesha top par hona chahiye
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files ke liye
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

# 🔥 UPDATE 4: CORS (Vercel ke live URL se request accept karne ke liye)
CORS_ALLOW_ALL_ORIGINS = False  # Isey hamesha False rakhein jab niche URLs define kiye hon
CORS_ALLOW_CREDENTIALS = True   # Ye True hona bohot zaroori hai JWT Tokens aur Login ke liye!

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  
    "http://localhost:5173",  
    "http://127.0.0.1:5500", 
    "http://127.0.0.1:5173",
    "https://smg-erp.duckdns.org",
    "https://shreemaa-frontend.vercel.app",
]

CSRF_TRUSTED_ORIGINS = [
    "https://smg-erp.duckdns.org",
    "https://shreemaa-frontend.vercel.app",
]

# (Optional safety) Headers aur methods allow karne ke liye
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept', 'accept-encoding', 'authorization', 'content-type', 'dnt',
    'origin', 'user-agent', 'x-csrftoken', 'x-requested-with',
]
# DRF & JWT Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

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

WSGI_APPLICATION = 'project.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# 🔥 UPDATE 5: Render par Static Files (CSS/JS) serve karne ka system
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'





