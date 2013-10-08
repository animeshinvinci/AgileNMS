from django.contrib import admin
import models


admin.site.register(models.Group)
admin.site.register(models.DummyMonitor)
admin.site.register(models.PingMonitor)
admin.site.register(models.TCPMonitor)
admin.site.register(models.HTTPMonitor)
admin.site.register(models.Check)
