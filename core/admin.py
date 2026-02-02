from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Manufacturer, Drug, Patient, Objaw, Zdarzenie

admin.site.register(Manufacturer)
admin.site.register(Drug)
admin.site.register(Patient)
admin.site.register(Objaw)
admin.site.register(Zdarzenie)