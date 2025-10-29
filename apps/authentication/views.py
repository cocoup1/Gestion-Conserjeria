

from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # Importamos messages para mostrar mensajes de error

from django.dispatch import receiver
from django.shortcuts import render, redirect

#from django.db import connection
from apps.authentication.models import(
Region, Comuna, Rol, Empleados
) 
from .forms import LoginForm, SignUpForm
import logging
from django.http import JsonResponse, HttpResponse

logger = logging.getLogger(__name__)


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":

        print(f'POST data:::::::::::::::::::: {request.POST}')
        print(f'Datos del formulario ::::::::::::::::::::: {dict(request.POST)}')
        

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(username=username, password=password)

            if user is not None:
                # Intentamos iniciar sesión y luego verificamos el rol del usuario
                login(request, user)
                request.session['username'] = user.username  # Almacenar el nombre de usuario en la sesión

                # Si el usuario es super_admin, omitimos la validación de empleado_id
                if user.is_super_admin():
                    return redirect("/")  # Redirige al menú o dashboard del sistema

                # Obtener el empleado asociado al usuario
                try:
                    empleado = Empleados.objects.get(usuario=user)
                    request.session['empleado_id'] = empleado.id

                    print(f"Nombres: {empleado.nombres}, Apellido: {empleado.apellido_paterno}")
                    request.session['nombre_empleado'] = (empleado.nombres + ' ' + empleado.apellido_paterno).title()

                except Empleados.DoesNotExist:
                    messages.error(request, "Debe registrar un empleado antes de iniciar sesión.")
                    return redirect("logout")  # Redirige a la vista de logout

                # Si el empleado está asociado, redirige a la página de inicio o dashboard
                return redirect("/")  # Redirige a la página de inicio u otra vista
            else:
                msg = 'Credenciales inválidas'
        else:
            msg = 'Error al validar el formulario'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})

# REGISTRO DE USUARIOS 
def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg = 'User created successfully.'
            success = True

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def logout_user(request):
    logout(request)
    return redirect("/login/")


def listar_empleados(request):
    # Aquí iría la lógica para obtener la lista de empleados
    empleados = []  # Reemplaza esto con la lógica real

    context = {
        'empleados': empleados,
        'submenu_open': True,  # Asegúrate de incluir esta clave
        'segment': 'listar-empleados'  # Incluye también esta clave
    }
    
    return render(request, 'home/listar-empleados.html', context)


