from django.contrib import admin
from geodata.models import GeoData, FailedWorkerResult

admin.site.register(GeoData)
admin.site.register(FailedWorkerResult)
