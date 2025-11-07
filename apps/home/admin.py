# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Prueba, TipoCondominio, Condominio, Residentes, Propiedad, UbicacionEstacionamiento, TipoEstacionamiento, Estacionamiento, ReservaEstacionamiento, EstadoEstacionamiento, NumeroEstacionamiento

# Register your models here.


admin.site.register(Prueba)
admin.site.register(TipoCondominio)
admin.site.register(Condominio)
admin.site.register(Residentes)
admin.site.register(Propiedad)
admin.site.register(UbicacionEstacionamiento)
admin.site.register(TipoEstacionamiento)
admin.site.register(Estacionamiento)
admin.site.register(ReservaEstacionamiento)
admin.site.register(EstadoEstacionamiento)
admin.site.register(NumeroEstacionamiento)



