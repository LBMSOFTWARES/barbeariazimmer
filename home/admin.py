from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Usuarios)
admin.site.register(Barbeiros)
admin.site.register(Servicos)
admin.site.register(Location)
admin.site.register(Expediente)
admin.site.register(Agendamentos)