from django.shortcuts import render, redirect, get_object_or_404
from django import template

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from django.template.loader import render_to_string
#from weasyprint import HTML

from .models import Prueba
from django.db.models import Q, Prefetch
from apps.authentication.models import Region, Comuna, Empleados, User  # Importar User desde apps.authentication.models
from apps.home.models import (
    Estacionamiento, TipoEstacionamiento, 
    UbicacionEstacionamiento, ReservaEstacionamiento, EstadoEstacionamiento,
    NumeroEstacionamiento, Propiedad, Residentes
)

from .forms import (
     PruebaForm, EmpleadoForm, EstacionamientoForm, 
     ReservaEstacionamientoForm, EmpleadoEditForm, 
     ProfileForm, ReservaEstacionamientoEditForm, ReservaEstacionamientoVerDetalleForm)

import logging

logger = logging.getLogger(__name__)

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

# ----------------- REGION, COMUNAS, NUMERO-EST. ---------------------------
# LLAMDAS AJAX
def load_regiones(request):
    logger.debug("Loading regions")
    regiones = Region.objects.all().values('id', 'nombre')
    logger.debug(f"Regiones: {list(regiones)}")
    return JsonResponse(list(regiones), safe=False)

def load_comunas(request):
    print('QUE VIENE EN COMUNAS ::::::::::::::::::::::::::', request)
    region_id = request.GET.get('region_id')
    comunas = Comuna.objects.filter(id_region=region_id).order_by('nombre')
    return JsonResponse(list(comunas.values('id', 'nombre')), safe=False)


# ----------------- SECCIÓN  CONSERJE GESTION ---------------------------

@login_required(login_url="/login/")
def ver_conserjes_view_sinfiltro(request):
    empleados = Empleados.objects.all()
    return render(request, 'home/ver-empleados.html', {'empleadosObj':empleados})


@login_required(login_url="/login/")
def ver_conserjes_view(request):
    query = Q()
    if 'rut' in request.GET and request.GET['rut']:
        query &= Q(rut__icontains=request.GET['rut'])
    if 'nombres' in request.GET and request.GET['nombres']:
        query &= (
            Q(nombres__icontains=request.GET['nombres']) |
            Q(apellido_paterno__icontains=request.GET['nombres']) |
            Q(apellido_materno__icontains=request.GET['nombres'])
        )
    if 'correo_electronico' in request.GET and request.GET['correo_electronico']:
        query &= Q(correo_electronico__icontains=request.GET['correo_electronico'])

    empleados = Empleados.objects.filter(query)
    return render(request, 'home/ver-empleados.html', {'empleadosObj': empleados})


@login_required(login_url="/login/")
def editar_conserje_view(request, id):   
    empleado = Empleados.objects.get(id=id)
    
    # Imprime todos los campos del objeto prueba en la consola
    for field in empleado._meta.fields:
        field_name = field.name
        field_value = getattr(empleado, field_name)
        print(f"{field_name}: {field_value}")

    formulario = EmpleadoEditForm(request.POST or None, instance=empleado)

    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('ver_conserjes')
    else:
        print("Errores del formulario:", formulario.errors)
        messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")
        
    return render(request, 'home/editar-conserje.html', {'formulario':formulario})


@login_required(login_url="/login/")
def eliminar_conserje_view(request, id):
    prueba = Empleados.objects.get(id=id)
    prueba.delete()
    return redirect('ver_conserjes') 
    
@login_required(login_url="/login/")
def exportar_conserjes_pdf(request):
    conserjes = Empleados.objects.all()
    html_string = render_to_string('home/pdf-empleados.html', {'empleados': conserjes})
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=conserjes.pdf'
    html.write_pdf(response)
    return response

@login_required(login_url="/login/")
def crear_conserje_view(request):
    print("Rol del usuario actual   :::::", request.user.role)
    formulario = EmpleadoForm(request.POST or None, user=request.user)
   
    msg = None
    success = False

    if request.method == "POST":
        print("viene del post ::::: " ,request.POST)
        
        if formulario.is_valid():
            print("formulario valido ::::: " ,formulario)
            # Tomar los campos del formulario de empleado
            rut = formulario.cleaned_data.get("rut")        
            nombres = formulario.cleaned_data.get("nombres")
            apellido_paterno = formulario.cleaned_data.get("apellido_paterno")
            apellido_materno = formulario.cleaned_data.get("apellido_materno")
            email = formulario.cleaned_data.get("correo_electronico")
            raw_password = formulario.cleaned_data.get("clave_temporal")  
            rol = formulario.cleaned_data.get("id_rol")

            # Generar el nombre de usuario a partir del primer nombre y el primer apellido
            base_username = f"{nombres.split()[0].lower()}.{apellido_paterno.lower()}"
            username = base_username
            counter = 1

            # Asegurarse de que el nombre de usuario sea único
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter:02d}"
                counter += 1

            # Validar que el rut no se repita en la tabla de empleados
            if Empleados.objects.filter(rut=rut).exists():
                msg = 'Empleado ya existe'
                return render(request, "home/registrar-conserje.html", {"formulario": formulario, "msg": msg, "success": success})

            # Validar que el correo de usuario no se repita en la tabla de usuarios
            if User.objects.filter(email=email).exists():
                msg = 'Correo electrónico ya existe'
                return render(request, "home/registrar-conserje.html", {"formulario": formulario, "msg": msg, "success": success})

            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=nombres,
                last_name=f"{apellido_paterno} {apellido_materno}"
            )
            user.set_password(raw_password)  # Encriptar la clave temporal
            user.rol = rol  # Asignar el id del rol al usuario
            user.role = rol.nombre  # Asignar el nombre del rol al usuario
            user.save()
            
            # Imprimir los datos del usuario y su ID
            print("Usuario creado ::::: ", user)
            print("ID del usuario creado ::::: ", user.id)
            
            # Crear el empleado asociado al usuario
            empleado = formulario.save(commit=False)
            empleado.usuario = user
            empleado.save()  # Guardar el empleado primero para obtener un ID

            # Guardar las relaciones de muchos a muchos
            formulario.save_m2m()

            msg = 'Usuario creado con exito'
            success = True

            return redirect('ver_conserjes')
      

    return render(request, "home/registrar-conserje.html",{"formulario": formulario, "msg": msg, "success": success})


# ------------------------ SECCIÓN ESTACIONAMIENTOS MANTENEDOR  --------------------

from django.db.models import Prefetch

@login_required(login_url="/login/")
def ver_estacionamientos_view(request):
    query = Q()
    if 'numero_estacionamiento' in request.GET and request.GET['numero_estacionamiento']:
        query &= Q(numero_estacionamiento__nombre=request.GET['numero_estacionamiento'])

    if 'ubicacion' in request.GET and request.GET['ubicacion']:
        query &= Q(ubicacion__nombre=request.GET['ubicacion'])

    if 'tipo_estacionamiento' in request.GET and request.GET['tipo_estacionamiento']:
        query &= Q(tipo_estacionamiento__nombre=request.GET['tipo_estacionamiento'])

    if 'estado_estacionamiento' in request.GET and request.GET['estado_estacionamiento']:
        query &= Q(estado_estacionamiento__nombre=request.GET['estado_estacionamiento'])

    # Filtrar los estacionamientos
    estacionamientos = Estacionamiento.objects.filter(query).select_related(
        'numero_estacionamiento',
        'ubicacion',
        'tipo_estacionamiento',
        'estado_estacionamiento'
    )

    # Obtener los valores únicos para los filtros basados en registros existentes en Estacionamiento
    numeros_estacionamiento = NumeroEstacionamiento.objects.filter(
        estacionamiento__isnull=False  # Relación inversa para validar existencia
    ).distinct()

    ubicaciones = UbicacionEstacionamiento.objects.filter(
        estacionamiento__isnull=False
    ).distinct()

    tipos_estacionamiento = TipoEstacionamiento.objects.filter(
        estacionamiento__isnull=False
    ).distinct()

    estados_estacionamiento = EstadoEstacionamiento.objects.filter(
        estacionamiento__isnull=False
    ).distinct()

    return render(request, 'home/ver-estacionamientos.html', {
        'estacionamientosObj': estacionamientos,
        'numeros_estacionamiento': numeros_estacionamiento,
        'ubicaciones': ubicaciones,
        'tipos_estacionamiento': tipos_estacionamiento,
        'estados_estacionamiento': estados_estacionamiento,
    })

@login_required(login_url="/login/")
def ver_estacionamientos_disponibles_view(request):
    if request.method == "GET":
        estacionamientos = Estacionamiento.objects.filter(estado_estacionamiento=1).select_related(
            'numero_estacionamiento', 'ubicacion', 'tipo_estacionamiento'
        )
        
        print("Estacionamientos disponibles 1:")
        for estacionamiento in estacionamientos:
            print(f"ID: {estacionamiento.id}, Número: {estacionamiento.numero_estacionamiento.nombre}, Ubicación: {estacionamiento.ubicacion.nombre}, Tipo: {estacionamiento.tipo_estacionamiento.nombre}")


        if estacionamientos.exists():
            estacionamientos_list = [
                {
                    'id': estacionamiento.id,
                    'numero': estacionamiento.numero_estacionamiento.nombre,
                    'ubicacion': estacionamiento.ubicacion.nombre,
                    'tipo': estacionamiento.tipo_estacionamiento.nombre,
                }
                for estacionamiento in estacionamientos
            ]

            print("Estacionamientos disponibles 2 :")
            for estacionamiento in estacionamientos_list:
                print(estacionamiento)

            return JsonResponse({'estacionamientos': estacionamientos_list}, status=200)
        else:
            return JsonResponse({'error': 'No hay estacionamientos disponibles'}, status=404)
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required(login_url="/login/")
def crear_estacionamiento_view(request):
    formulario = EstacionamientoForm(request.POST or None)

    if request.method == 'POST':
        print(request.POST)
    
        if formulario.is_valid():
            estacionamiento = formulario.save()
            # Actualizar el estado del NumeroEstacionamiento
            numero_estacionamiento = estacionamiento.numero_estacionamiento
            numero_estacionamiento.estado = '0'
            numero_estacionamiento.save()
            return redirect('ver_estacionamientos')
        else:
            messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")

            print("Errores del formulario:", formulario.errors)

    return render(request, 'home/registrar-estacionamiento.html',{'formulario':formulario})


@login_required(login_url="/login/")
def editar_estacionamiento_view(request, id):   
    estacionamiento = Estacionamiento.objects.get(id=id)
    
    # Imprime todos los campos del objeto prueba en la consola
    for field in estacionamiento._meta.fields:
        field_name = field.name
        field_value = getattr(estacionamiento, field_name)
        print(f"{field_name}: {field_value}")

    formulario = EstacionamientoForm(request.POST or None, instance=estacionamiento)

    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('ver_estacionamientos')
    else:
        print("Errores del formulario:", formulario.errors)
        messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")
  
    return render(request, 'home/editar-estacionamiento.html', {
    'formulario': formulario,
    'numero_estacionamiento': estacionamiento.numero_estacionamiento.nombre,
    'ubicacion_estacionamiento': estacionamiento.ubicacion.nombre
})


# -------------- SECCIÓN RESERVAS ----------------------------

@login_required(login_url="/login/")
def buscar_residentes(request):
    numero_propiedad = request.GET.get('numero_propiedad')
    if numero_propiedad:
        try:
            propiedad = Propiedad.objects.get(numero_propiedad=numero_propiedad)
            residentes = Residentes.objects.filter(propiedad=propiedad)
            residentes_list = [{'id': residente.id, 'nombre': f'{residente.nombres} {residente.apellido_paterno} {residente.apellido_materno}'} for residente in residentes]
            return JsonResponse({'residentes': residentes_list})
        except Propiedad.DoesNotExist:
            return JsonResponse({'error': 'Propiedad no encontrada'}, status=404)
    return JsonResponse({'error': 'Número de propiedad no proporcionado'}, status=400)

@login_required(login_url="/login/")
def obtener_datos_residente(request):   
    residente_id = request.GET.get('residente_id')
    if residente_id:
        try:
            residente = Residentes.objects.get(id=residente_id)
            datos_residente = {
                'id': residente.id,
                'nombre_completo': f'{residente.nombres} {residente.apellido_paterno} {residente.apellido_materno}',
                'telefono': residente.telefono
            }
            return JsonResponse(datos_residente)
        except Residentes.DoesNotExist:
            return JsonResponse({'error': 'Residente no encontrado'}, status=404)
    return JsonResponse({'error': 'ID de residente no proporcionado'}, status=400)

@login_required(login_url="/login/")
def obtener_datos_propiedad(request):    
    numero_propiedad = request.GET.get('numero_propiedad')
    if numero_propiedad:
        try:
            propiedad = Propiedad.objects.get(numero_propiedad=numero_propiedad)
            print("Propiedad ::::::::::::::::::::::.....: ", propiedad)
            datos_propiedad = {
                'id': propiedad.id,
                'numero_propiedad': propiedad.numero_propiedad,
                'piso': propiedad.piso,
                'estado': propiedad.estado
            }
            return JsonResponse(datos_propiedad)
        except Propiedad.DoesNotExist:
            return JsonResponse({'error': 'Propiedad no encontrada'}, status=404)
    return JsonResponse({'error': 'Número de propiedad no proporcionado'}, status=400)


@login_required(login_url="/login/")
def ver_reservas_view(request):
    # Imprimir el contenido del request GET en la consola
    print("Request GET data:", request.GET)

    query = Q()
    if 'rut_visita' in request.GET and request.GET['rut_visita']:
        query &= Q(rut_visita__icontains=request.GET['rut_visita'])

    if 'patente_vehiculo' in request.GET and request.GET['patente_vehiculo']:
        query &= Q(patente_vehiculo__icontains=request.GET['patente_vehiculo'])

    if 'estado_estacionamiento' in request.GET and request.GET['estado_estacionamiento']:
        query &= Q(estado_estacionamiento__icontains=request.GET['estado_estacionamiento'])

    reservas = ReservaEstacionamiento.objects.filter(query)

    # Obtener los datos de las reservas, el número de estacionamiento, ubicación si existe
    reservas_list = []
    for reserva in reservas:
        numero_estacionamiento = ''
        ubicacion_estacionamiento = ''

        if reserva.estacionamiento:
            try:
                estacionamiento = Estacionamiento.objects.get(id=reserva.estacionamiento)
                numero_estacionamiento = estacionamiento.numero_estacionamiento.nombre
                ubicacion_estacionamiento = estacionamiento.ubicacion.nombre
            except Estacionamiento.DoesNotExist:
                numero_estacionamiento = 'No aplica'
                ubicacion_estacionamiento = 'No aplica 2'

        reservas_list.append({
            'id': reserva.id,
            'rut_visita': reserva.rut_visita,
            'nombre_completo': f"{reserva.nombre_visita} {reserva.apellido_paterno_visita}",
            'relacion_residente': reserva.relacion_residente,
            'patente_vehiculo': reserva.patente_vehiculo,
            'descripcion_vehiculo': reserva.descripcion_vehiculo,
            'numero_estacionamiento': numero_estacionamiento,
            'fecha_registro_visita': reserva.fecha_registro_visita,
            'estado_estacionamiento': reserva.estado_estacionamiento,
            'ubicacion_estacionamiento': ubicacion_estacionamiento,
            'fecha_llegada_visita': reserva.fecha_llegada_visita,
            'fecha_fin_visita': reserva.fecha_fin_visita
        })

    # Obtener los valores únicos del campo estado_estacionamiento
    estados_estacionamiento = ReservaEstacionamiento.objects.values_list('estado_estacionamiento', flat=True).distinct()
     
    return render(request, 'home/ver-reservas.html', {
        'reservasObj': reservas_list,
        'estados_estacionamiento': estados_estacionamiento
    })

@login_required(login_url="/login/")
def ver_reservas_view(request):
    print('Request del get ::::::::: ', request.GET)
    query = Q()
    if 'rut_visita' in request.GET and request.GET['rut_visita']:
        query &= Q(rut_visita=request.GET['rut_visita'])

    if 'patente_vehiculo' in request.GET and request.GET['patente_vehiculo']:
        query &= Q(patente_vehiculo=request.GET['patente_vehiculo'])

    if 'estado_estacionamiento' in request.GET and request.GET['estado_estacionamiento']:
        query &= Q(estado_estacionamiento=request.GET['estado_estacionamiento'])

    reservas = ReservaEstacionamiento.objects.filter(query)

    # Obtener los datos de las reservas, el número de estacionamiento, ubicación si existe
    reservas_list = []
    for reserva in reservas:
        numero_estacionamiento = ''
        ubicacion_estacionamiento = ''

        if reserva.estacionamiento:
            try:
                estacionamiento = Estacionamiento.objects.get(id=reserva.estacionamiento)
                numero_estacionamiento = estacionamiento.numero_estacionamiento.nombre
                ubicacion_estacionamiento = estacionamiento.ubicacion.nombre
            except Estacionamiento.DoesNotExist:
                numero_estacionamiento = 'No aplica'
                ubicacion_estacionamiento = 'No aplica 2'

        reservas_list.append({
            'id': reserva.id,
            'rut_visita': reserva.rut_visita,
            'nombre_completo': f"{reserva.nombre_visita} {reserva.apellido_paterno_visita}",
            'relacion_residente': reserva.relacion_residente,
            'patente_vehiculo': reserva.patente_vehiculo,
            'descripcion_vehiculo': reserva.descripcion_vehiculo,
            'numero_estacionamiento': numero_estacionamiento,
            'fecha_registro_visita': reserva.fecha_registro_visita,
            'estado_estacionamiento': reserva.estado_estacionamiento,
            'ubicacion_estacionamiento': ubicacion_estacionamiento,
            'fecha_llegada_visita': reserva.fecha_llegada_visita,
            'fecha_fin_visita': reserva.fecha_fin_visita
        })

    # Obtener los valores únicos del campo estado_estacionamiento
    estados_estacionamiento = ReservaEstacionamiento.objects.values_list('estado_estacionamiento', flat=True).distinct()

    return render(request, 'home/ver-reservas.html', {
        'reservasObj': reservas_list,
        'estados_estacionamiento': estados_estacionamiento
    })

@login_required(login_url="/login/")
def crear_reserva_view(request):
    msg = None

    # Obtenemos el formulario con los datos POST si están presentes
    empleado_id = request.session.get('empleado_id')
    initial_data = {'empleado_id': empleado_id}

    formulario = ReservaEstacionamientoForm(request.POST or None)
    numero_propiedad = request.POST.get('propiedad', '').strip() or request.GET.get('numero_propiedad', '').strip()

    if numero_propiedad is not None:
        try:
            if isinstance(numero_propiedad, dict):
                numero_propiedad = numero_propiedad.get('id')
                numero_propiedad = int(numero_propiedad)

        except ValueError:
            print("Error: numero_propiedad no es un número válido.")
            numero_propiedad = None
            msg = 'numero_propiedad no es un número válido'
    else:
        print("Error: numero_propiedad es None.")
        numero_propiedad = None

    residentes = None  # Inicializar la variable residentes
   
    if numero_propiedad:
        propiedad = Propiedad.objects.get(id=numero_propiedad)       
        datos_propiedad = {
                'id': propiedad.id,
                'numero_propiedad': propiedad.numero_propiedad,
                'piso': propiedad.piso,
                'estado': propiedad.estado
        }
        print("Propiedad resultado ::::::::::::::::::::::.....: ", datos_propiedad)

        # Iterar sobre las claves y valores del diccionario
        for key, value in datos_propiedad.items():
            print(f"{key}: {value}")

        residentes = Residentes.objects.filter(propiedad=datos_propiedad['id'])
        
        # Iterar sobre los objetos del QuerySet de Residentes
        for residente in residentes:
            print(f"Residente ID: {residente.id}, Nombre: {residente.nombres}, Propiedad ID: {residente.propiedad.id}")
        print("residentes despues del for ::::::::::::::::::::::.....: ", residentes)
        # Asigna el queryset de residentes a los campos del formulario
        formulario.fields['residente'].queryset = residentes

        if request.method == 'GET':
            # Configura los valores iniciales para el formulario
            formulario = ReservaEstacionamientoForm(initial={
                'propiedad': propiedad.id,
                'nombre_visita': residentes[0].nombres if residentes else '',
                'apellido_paterno_visita': residentes[0].apellido_paterno if residentes else '',
                'apellido_materno_visita': residentes[0].apellido_materno if residentes else '',
                'telefono_visita': residentes[0].telefono if residentes else '',
            })

        elif request.method == 'POST':

            id_residente2 = request.POST.get('id_residente2', '').strip()
            if not id_residente2:
                msg = "El ID del residente no puede estar vacío. xxxxxx"
                print("Error: El ID del residente no está presente.")

            if not msg:
                formulario = ReservaEstacionamientoForm(request.POST or None)
          
                if formulario.is_valid():
                    reserva = formulario.save(commit=False)

                    # Asigna el ID del empleado logueado
                    reserva.empleado_id = empleado_id
                    reserva.id_residente2 = id_residente2

                    #Si el registro es de visita, no se asigna estacionamiento
                    if reserva.estacionamiento:
                        reserva.estado_estacionamiento = 'Reservado'
                    else:
                        reserva.estado_estacionamiento = 'Sin estacionamiento'

                    if reserva.patente_vehiculo:
                        reserva.patente_vehiculo = reserva.patente_vehiculo.upper()
                    else:
                        reserva.patente_vehiculo = ' '

                    #reserva.fecha_registro_visita = timezone.now()
                    reserva.save()  # Guarda la reserva

                    # Actualizar el estado del estacionamiento a reservado
                    if reserva.estacionamiento:
                        estacionamiento = get_object_or_404(Estacionamiento, id=reserva.estacionamiento)
                        estacionamiento.estado_estacionamiento = EstadoEstacionamiento.objects.get(id=3)  # Estado reservado
                        estacionamiento.save()
                        
                        # Actualizar el estado del número de estacionamiento a 0 (no disponible)
                        numero_estacionamiento = estacionamiento.numero_estacionamiento
                        numero_estacionamiento.estado = '0'
                        numero_estacionamiento.save()

                    return redirect('ver_reservas')
                else:
                    messages.error(request, "Errores en el formulario. Por favor corrígelos.")
                    print("Errores del formulario:", formulario.errors)
                    msg = formulario.errors
            else:
                msg = "Errores en el formulario. Por favor corrígelos."
        else:
            formulario = ReservaEstacionamientoForm()

        return render(request, 'home/registrar-reserva.html', {'formulario': formulario, 'residentes': residentes, 'msg':msg})

    return render(request, 'home/registrar-reserva.html', {'formulario': formulario, 'residentes': residentes, 'msg': msg})

@login_required(login_url="/login/")
def confirmar_reserva_view(request, id):
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    
    # Actualizar el estado del estacionamiento a ocupado
    if reserva.estacionamiento:
        estacionamiento = get_object_or_404(Estacionamiento, id=reserva.estacionamiento)
        estacionamiento.estado_estacionamiento = EstadoEstacionamiento.objects.get(nombre='Ocupado')
        estacionamiento.save()
        
        # Actualizar campo fecha_llegada_visita con la fecha y hora actual
        reserva.fecha_llegada_visita = timezone.now()
        reserva.estado_estacionamiento = 'Ocupado'
    
    # Actualizar la reserva
    reserva.save()
    
    messages.success(request, 'Reserva confirmada exitosamente.')
    return redirect('ver_reservas')

@login_required(login_url="/login/")
def confirmar_reserva_visita_view(request, id):
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    reserva.fecha_llegada_visita = timezone.now()
    reserva.save()
    
    messages.success(request, 'Reserva confirmada exitosamente.')
    return redirect('ver_reservas')

#Modifica algunos datos, puede o no cambiar de estacionamiento
@login_required(login_url="/login/")
def editar_reserva_view(request, id):
    # Obtener la reserva
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    propiedad = reserva.propiedad

    # Imprimir información de la reserva
    print("Información de la reserva:")
    print(f"ID: {reserva.id}")
    print(f"Propiedad: {propiedad}")
    print(f"Estacionamiento: {reserva.estacionamiento}")
    print(f"Patente Vehículo: {reserva.patente_vehiculo}")
    print(f"Fecha Llegada Visita: {reserva.fecha_llegada_visita}")
    print(f"Tiempo Permanencia: {reserva.tiempo_permanencia}")


    # Obtener información del estacionamiento basado en el id
    estacionamiento = None
    numero_estacionamiento = "Sin asignar"
    ubicacion_estacionamiento = "Sin asignar"
    llave_estacionamiento = None

    if reserva.estacionamiento:  # Solo buscar si el ID del estacionamiento no es None
        try:
            estacionamiento = Estacionamiento.objects.get(id=reserva.estacionamiento)
            numero_estacionamiento = estacionamiento.numero_estacionamiento.nombre
            ubicacion_estacionamiento = estacionamiento.ubicacion.nombre
            llave_estacionamiento = estacionamiento.id 

            # Imprimir información del estacionamiento
            print("Información del estacionamiento:")
            print(f"ID: {estacionamiento.id}")
            print(f"Número Estacionamiento: {numero_estacionamiento}")
            print(f"Ubicación Estacionamiento: {ubicacion_estacionamiento}")

        except Estacionamiento.DoesNotExist:
            pass  # Mantener los valores por defecto si no existe el estacionamiento

    # Obtener la información del residente
    try:
        residente = Residentes.objects.get(id=reserva.id_residente2)
    
        print("Información del residente:")
        print(f"ID: {residente.id}")
        print(f"Nombre: {residente.nombres} {residente.apellido_paterno} {residente.apellido_materno}")
 
    except Residentes.DoesNotExist:
        residente = None  # Si no hay residente asociado, asignar None

    # Procesamiento del formulario al recibir una solicitud POST

    if request.method == 'POST':
        print(" 3 rquest post ::::::::::::::: ", request.POST)

        formulario = ReservaEstacionamientoEditForm(request.POST, instance=reserva)
        if formulario.is_valid():
            llave_estacionamiento = formulario.cleaned_data.get('llave_estacionamiento')
            print(f"Valor del campo oculto: {llave_estacionamiento}")
            reserva = formulario.save(commit=False)

            # 0. validar si el campo estacionamiento viene vacio o null. Si es asi, no actauliza estacionamiento.
            estacionamiento_id = request.POST.get('estacionamiento')

            if reserva.estacionamiento:
               
               if estacionamiento_id:   
                    # 1. Actualiza la reserva con un  estacionamiento nuevo (actualiza el campo estado = 3(reservado) y el campo estado = 0 de la tabla numeroestacionamiento)                
                    try:
                        estacionamiento = Estacionamiento.objects.get(id=reserva.estacionamiento)
                        estacionamiento.estado_estacionamiento = EstadoEstacionamiento.objects.get(nombre='Reservado')#Id=3
                        estacionamiento.save()

                        # Actualizar el estado del número de estacionamiento a 0 (no disponible)
                        numero_estacionamiento = estacionamiento.numero_estacionamiento
                        numero_estacionamiento.estado = '0'
                        numero_estacionamiento.save()

                        # 2. Cambia el estado del estacionamiento anterior a disponible y el numero de estacionamiento a 1 (en su tabla numeroestacionamiento)
                        estacionamiento = Estacionamiento.objects.get(id=llave_estacionamiento)
                        estacionamiento.estado_estacionamiento = EstadoEstacionamiento.objects.get(nombre='Disponible') 
                        estacionamiento.save()

                        numero_estacionamiento = estacionamiento.numero_estacionamiento
                        numero_estacionamiento.estado = '1'
                        numero_estacionamiento.save()

                    except Estacionamiento.DoesNotExist:
                        messages.warning(request, "El estacionamiento asociado no existe.")

            else:
                print("No se proporcionó un estacionamiento en el formulario.") 
                reserva.estacionamiento = llave_estacionamiento

            #Si el registro es solo de Reserva
            if reserva.patente_vehiculo:
                reserva.patente_vehiculo = reserva.patente_vehiculo.upper()

            reserva.fecha_modifica_reserva = timezone.now()   
            reserva.save()

            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('ver_reservas')
        else:
            messages.error(request, "Errores en el formulario. Por favor corrígelos.")
            print("Errores del formulario:", formulario.errors)
            msg = formulario.errors
    else:
        formulario = ReservaEstacionamientoEditForm(instance=reserva)
   
    
    return render(request, 'home/editar-reserva.html', {
        'formulario': formulario,
        'reserva': reserva,
        'propiedad': propiedad,
        'numero_estacionamiento': numero_estacionamiento,
        'ubicacion_estacionamiento': ubicacion_estacionamiento,
        'llave_estacionamiento': llave_estacionamiento,
        'residente': residente
    })

@login_required(login_url="/login/")
def detalle_reserva_view(request, id):
    # Obtener la reserva
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    propiedad = reserva.propiedad

    # Obtener información del estacionamiento basado en el id
    estacionamiento = None
    numero_estacionamiento = "Sin asignar"
    ubicacion_estacionamiento = "Sin asignar"
    llave_estacionamiento = None

    if reserva.estacionamiento:  # Solo buscar si el ID del estacionamiento no es None
        try:
            estacionamiento = Estacionamiento.objects.get(id=reserva.estacionamiento)
            numero_estacionamiento = estacionamiento.numero_estacionamiento.nombre
            ubicacion_estacionamiento = estacionamiento.ubicacion.nombre
            llave_estacionamiento = estacionamiento.id 

        except Estacionamiento.DoesNotExist:
            pass  # Mantener los valores por defecto si no existe el estacionamiento

    # Obtener la información del residente
    try:
        residente = Residentes.objects.get(id=reserva.id_residente2)
    except Residentes.DoesNotExist:
        residente = None  # Si no hay residente asociado, asignar None

    formulario = ReservaEstacionamientoVerDetalleForm(instance=reserva)
    
    return render(request, 'home/ver-reserva-detalle.html', {
        'formulario': formulario,
        'reserva': reserva,
        'propiedad': propiedad,
        'numero_estacionamiento': numero_estacionamiento,
        'ubicacion_estacionamiento': ubicacion_estacionamiento,
        'llave_estacionamiento': llave_estacionamiento,
        'residente': residente
    })

@login_required(login_url="/login/")
def finalizar_reserva_view(request, id):
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    empleado_id = request.session.get('empleado_id')
    
    # Actualizar el estado del estacionamiento a disponible u ocupado
    if reserva.estacionamiento:
        estacionamiento = get_object_or_404(Estacionamiento, id=reserva.estacionamiento)
        
        # Verificar el estado actual del estacionamiento
        if estacionamiento.estado_estacionamiento.nombre in ['Ocupado', 'Reservado']:
            estacionamiento.estado_estacionamiento = EstadoEstacionamiento.objects.get(nombre='Disponible')
            estacionamiento.save()
        
        # Actualizar el estado del número de estacionamiento a 0 (disponible)
        numero_estacionamiento = estacionamiento.numero_estacionamiento
        numero_estacionamiento.estado = '1'
        numero_estacionamiento.save()
    else:
        print("No se proporcionó un estacionamiento en la reserva.  SOY VISITA")


    # Finliza  la reserva y actauliza el estado de la reserva
    reserva.empleado_id = empleado_id
    reserva.estado_estacionamiento = 'Finalizado'
    reserva.fecha_fin_visita = timezone.now()
    reserva.save()
    
    messages.success(request, 'La reserva ha sido eliminada exitosamente.')
    return redirect('ver_reservas')

@login_required(login_url="/login/")
def finalizar_reserva_visita_view(request, id):
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    empleado_id = request.session.get('empleado_id')
    
    reserva.empleado_id = empleado_id
    reserva.fecha_fin_visita = timezone.now()
    reserva.save()
    
    messages.success(request, 'La reserva ha sido finalizada exitosamente.')
    return redirect('ver_reservas')

@login_required(login_url="/login/")
def eliminar_reserva_view(request, id):
    reserva = get_object_or_404(ReservaEstacionamiento, id=id)
    empleado_id = request.session.get('empleado_id')
    
    # Actualizar el estado del estacionamiento a disponible u ocupado
    if reserva.estacionamiento:
        estacionamiento = get_object_or_404(Estacionamiento, id=reserva.estacionamiento)
        
        # Verificar el estado actual del estacionamiento
        if estacionamiento.estado_estacionamiento.nombre in ['Ocupado', 'Reservado']:
            estacionamiento.estado_estacionamiento = EstadoEstacionamiento.objects.get(nombre='Disponible')
            estacionamiento.save()
        
        # Actualizar el estado del número de estacionamiento a 1 (disponible)
        numero_estacionamiento = estacionamiento.numero_estacionamiento
        numero_estacionamiento.estado = '1'
        numero_estacionamiento.save()
    else:
        print("No se proporcionó un estacionamiento en la reserva.  SOY VISITA")

    # Eliminar la reserva
    reserva = ReservaEstacionamiento.objects.get(id=id)
    reserva.delete()
    
    messages.success(request, 'La reserva ha sido eliminada exitosamente.')
    return redirect('ver_reservas')


@login_required(login_url="/login/")
def exportar_reservas_pdf(request):
    # Construcción del filtro para reservas
    query = Q()
    if 'rut_visita' in request.GET and request.GET['rut_visita']:
        query &= Q(rut_visita=request.GET['rut_visita'])

    if 'patente_vehiculo' in request.GET and request.GET['patente_vehiculo']:
        query &= Q(patente_vehiculo=request.GET['patente_vehiculo'])

    reservas = ReservaEstacionamiento.objects.filter(query)

    # Obtener los datos de las reservas con número y ubicación del estacionamiento
    reservas_list = []
    for reserva in reservas:
        numero_estacionamiento = ''
        ubicacion_estacionamiento = ''

        if reserva.estacionamiento:
            try:
                estacionamiento = Estacionamiento.objects.get(id=reserva.estacionamiento)
                numero_estacionamiento = estacionamiento.numero_estacionamiento.nombre
                ubicacion_estacionamiento = estacionamiento.ubicacion.nombre
            except Estacionamiento.DoesNotExist:
                numero_estacionamiento = 'No aplica'
                ubicacion_estacionamiento = 'No aplica'

        reservas_list.append({
            'id': reserva.id,
            'rut_visita': reserva.rut_visita,
            'nombre_completo': f"{reserva.nombre_visita} {reserva.apellido_paterno_visita}",
            'relacion_residente': reserva.relacion_residente,
            'patente_vehiculo': reserva.patente_vehiculo,
            'descripcion_vehiculo': reserva.descripcion_vehiculo,
            'numero_estacionamiento': numero_estacionamiento,
            'fecha_registro_visita': reserva.fecha_registro_visita,
            'estado_estacionamiento': reserva.estado_estacionamiento,
            'ubicacion_estacionamiento': ubicacion_estacionamiento,
            'fecha_llegada_visita': reserva.fecha_llegada_visita,
            'fecha_fin_visita': reserva.fecha_fin_visita,
        })

    # Renderizar la plantilla para generar el PDF
    html_string = render_to_string('home/pdf-reservas.html', {'reservas': reservas_list})

    # Generar el PDF
    base_url = request.build_absolute_uri('/')
    html = HTML(string=html_string, base_url=base_url)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=reservas.pdf'
    html.write_pdf(response)

    return response


# ----------------- RUTAS PARA IR A LAS PAGINAS  DE OBSERVACIONES ---------------------------

@login_required(login_url="/login/")
def ver_observaciones_view(request):
    pruebas = Prueba.objects.all()
    print(pruebas)
    return render(request,'home/ver-observaciones.html', {'pruebasObj':pruebas})
    

@login_required(login_url="/login/")
def crear_observacion_view(request):
    formulario = PruebaForm(request.POST or None)
    if formulario.is_valid():
        formulario.save()
        return redirect('ver_observaciones') # aca estoy llamado a la url del home : 'ver_observaciones'

    return render(request, 'home/registrar-observacion.html', {'formulario':formulario})


@login_required(login_url="/login/")
def editar_observacion_view(request, id):
    prueba = Prueba.objects.get(id=id)
    
    # Imprime todos los campos del objeto prueba en la consola
    for field in Prueba._meta.fields:
        field_name = field.name
        field_value = getattr(prueba, field_name)
        print(f"{field_name}: {field_value}")

    formulario = PruebaForm(request.POST or None, instance=prueba)

    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('ver_observaciones')

    return render(request, 'home/editar-observacion.html', {'formulario':formulario})


@login_required(login_url="/login/")
def eliminar_observacion_view(request, id):
    obj = Prueba.objects.get(id=id)
    obj.delete()
    return redirect('ver_observaciones') 
    


@login_required(login_url="/login/")
def profile_view(request):
    user = request.user
    if request.method == "POST":
        print("request.POST ::::: ", request.POST)
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # este emnsaje es el sweetalert exito
            #messages.success(request, 'La contraseña se ha actualizado con éxito.')
            return redirect('/')
        #else:
            #form.errors.clear()
            # por ahora no se usa gatilla cunado hay erro levanta sweetalert
            #messages.error(request, 'Por favor, corrija los errores.')
    else:
        print("request.GET ::::: ", request.GET)
        form = ProfileForm(instance=user)
    return render(request, 'home/profile.html', {'form': form})
