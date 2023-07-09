from django.contrib import admin

from . import models

admin.site.register(models.State)
admin.site.register(models.Location)
admin.site.register(models.Institution)
admin.site.register(models.User)
admin.site.register(models.UserInfo)
admin.site.register(models.Vendor)
admin.site.register(models.SubscriptionHistory)