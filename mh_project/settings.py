import os
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'inference',
    'rest_framework',
    'rest_framework.authtoken',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
   
}

ROOT_URLCONF = 'mh_project.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'inference', 'templates')],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'mh_project.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3','NAME': os.path.join(BASE_DIR, 'db.sqlite3')}}
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
STATIC_URL = '/static/'

LOGIN_URL = reverse_lazy('/login/')
LOGIN_REDIRECT_URL = reverse_lazy('/')
LOGOUT_REDIRECT_URL = reverse_lazy('/login/')