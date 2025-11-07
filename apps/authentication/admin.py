

from django.contrib import admin
from .models import Rol, Region, Comuna, Empleados, User


admin.site.register(Rol)
admin.site.register(Region)
admin.site.register(Comuna)
admin.site.register(Empleados)
admin.site.register(User)
