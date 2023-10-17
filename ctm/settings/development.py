from .base import *
DEBUG = True

ALLOWED_HOSTS = ['*']

SECRET_KEY = "django-insecure-gi5bknhnt_k4=-b-it8qq0x9ug&a+8zja96)=*cu=8q92$k0ic"

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': "ctm",
    'USER': "postgres",
    'PASSWORD': "Azeezat1@",
    'HOST': "127.0.0.1",
    'PORT': '',
  }
}

TAILWIND_MIDDLEWARE = [
  # TAILWIND
  "django_browser_reload.middleware.BrowserReloadMiddleware",
]

MIDDLEWARE += TAILWIND_MIDDLEWARE
MEDIA_ROOT = "C:\pycharm\django_project\storage\ctm\media"