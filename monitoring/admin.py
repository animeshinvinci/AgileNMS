from django.contrib import admin
import models


admin.site.register(models.Group)
admin.site.register(models.Monitor)
admin.site.register(models.Check)
admin.site.register(models.Result)
