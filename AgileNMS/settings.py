# PROJECT ROOT
import os
PROJECT_DIR = os.path.join(os.path.dirname(__file__), os.pardir)
HTDOCS_DIR = os.path.join(PROJECT_DIR, "htdocs")

# DEBUG SETTINGS
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# ADMINS
ADMINS = ( )
MANAGERS = ADMINS

#DATABASE
import dj_database_url
DATABASES = { "default": dj_database_url.config(default = "sqlite:///db/test.db") }

# HOSTNAME AND ALLOWED_HOSTS
#HOSTNAME = "nms.agilenetworking.co.uk"
#ALLOWED_HOSTS = [HOSTNAME]

# LOCATION
TIME_ZONE = "Europe/London"
LANGUAGE_CODE = "en-gb"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# MEDIA
MEDIA_ROOT = os.path.join(HTDOCS_DIR, "media")
MEDIA_URL = "/media/"

# STATIC FILES
STATIC_ROOT = os.path.join(HTDOCS_DIR, "static")
STATIC_URL = "/static/"
STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "static"),
)
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# SECRET KEY
SECRET_KEY = "m0hr!2*973kk$003=n-73ehzf1e37sdh#2&jx2#w$^xt=_+hb+"

# MIDDLEWARE
MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
)

# TEMPLATES
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)
TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, "templates"),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
)

# URLS
ROOT_URLCONF = "AgileNMS.urls"

# WSGI
WSGI_APPLICATION = "AgileNMS.wsgi.application"

# INSTALLED APPS
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "djcelery",
    "bootstrapform",
    "monitoring",
)

# LOGGING
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}

# CELERY
import djcelery
djcelery.setup_loader()
CELERY_ALWAYS_EAGER = DEBUG
