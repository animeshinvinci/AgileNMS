# DO NOT EDIT THIS FILE UNLESS YOU KNOW WHAT YOU'RE DOING
# Please make a copy of this file and call it "local-settings.py" and edit that instead

# CELERY
CELERY_ALWAYS_EAGER = True

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    "run-checks-every-5-minutes": {
        "task": "monitoring.tasks.run_checks",
        "schedule": timedelta(seconds=5),
    },
    "update-every-minute": {
        "task": "monitoring.tasks.update",
        "schedule": timedelta(seconds=1),
    }
}

# Devserver and debug toolbar
EXTRA_INSTALLED_APPS = ("devserver", "debug_toolbar")
EXTRA_MIDDLEWARE_CLASSES = (
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)
INTERNAL_IPS = ("127.0.0.1",)