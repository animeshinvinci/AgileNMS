# DEBUG SETTINGS
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# ADMINS
ADMINS = ( )
MANAGERS = ADMINS

# DATABASES
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "agilenms",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "", # Set to empty string for localhost.
        "PORT": "", # Set to empty string for default.
    }
}

# HOSTNAME AND ALLOWED_HOSTS
HOSTNAME = "nms.agilenetworking.co.uk"
ALLOWED_HOSTS = [HOSTNAME]

# CELERY
from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    "run-checks-every-5-minutes": {
        "task": "monitoring.tasks.run_checks",
        "schedule": timedelta(minutes=5),
    },
    "update-every-minute": {
        "task": "monitoring.tasks.update",
        "schedule": timedelta(minutes=1),
    },
    "send-notifications-every-minute": {
        "task": "monitoring.tasks.send_notifications",
        "schedule": timedelta(minutes=1),
    },
}