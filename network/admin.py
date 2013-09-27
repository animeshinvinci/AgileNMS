from django.contrib import admin
import models


admin.site.register(models.PingPoller)
admin.site.register(models.TCPPoller)
admin.site.register(models.HTTPPoller)
admin.site.register(models.PingPollerResult)
admin.site.register(models.TCPPollerResult)
admin.site.register(models.HTTPPollerResult)
