from django.contrib import admin
import models


admin.site.register(models.Contact)
admin.site.register(models.PingPoller)
admin.site.register(models.HTTPPoller)
admin.site.register(models.PingPollerResult)
admin.site.register(models.HTTPPollerResult)
admin.site.register(models.Problem)
