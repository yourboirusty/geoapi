from django.contrib import admin
from data.models import GeoData, FailedWorkerResult

admin.site.register(GeoData)
admin.site.register(FailedWorkerResult)
