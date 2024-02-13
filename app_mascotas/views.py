from django.shortcuts import render, redirect, get_object_or_404
from .models import Propietario, Cuidador, Servicio, Mascota, DetPrestacion, Mensaje, Resena
from .forms import frmRegistro, frmLogin, frmCuidador, frmEdit, frmServicio, frmMascota, frmDetPrestacion, frmResena, frmEspecie, frmRaza, frmTipoServicio
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.db import connection
from django.utils import timezone

# Create your views here.
def index(request):
    default_page = 1
    page = request.GET.get('page', default_page)
    obtener = Servicio.objects.filter(es_activo=True).order_by('-id_servicio')
    query = request.GET.get('q')  # Obtener el término de búsqueda del request
    
    if query:
        # Filtrar mantenciones en función de la búsqueda
        obtener = obtener.filter(
            Q(tipo_servicio__tipo_servicio__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(precio__icontains=query) |
            Q(cuidador__especializacion__icontains=query) |
            Q(cuidador__propietario__username__icontains=query)  
        )

    items_per_page = 3  # Ajusta el número de elementos por página según tus necesidades
    paginator = Paginator(obtener, items_per_page)

    try:
        obtener = paginator.page(page)
    except PageNotAnInteger:
        obtener = paginator.page(default_page)
    except EmptyPage:
        obtener = paginator.page(paginator.num_pages)

    contexto = {
        'obtener': obtener,
    }
    return render(request, 'app_mascotas/index.html', contexto)



def registro(request):
    if request.method == 'POST':
        form = frmRegistro(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            user.save()
            messages.success(request,"Cuenta creada!")
            return redirect('index')  # Redirigir a la página de inicio después del registro
    else:
        form = frmRegistro()
    
    contexto = {
        'form': form,
    }
        
    return render(request, 'registration/registro.html', contexto)


def login_custom(request):
    if request.method == 'POST':
        form = frmLogin(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')  # Redirigir a la página de inicio después de iniciar sesión
    else:
        form = frmLogin()
    
    return render(request, 'registration/login_custom.html', {'form': form})


def logout_custom(request):
    logout(request)
    return redirect('index')


@login_required
def cuidador(request):
    form=frmCuidador(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmCuidador(data=request.POST,files=request.FILES)
        if form.is_valid():
           propietario = request.user  # Suponiendo que el usuario actual está autenticado
           cuidador = form.save(commit=False)
           cuidador.propietario = propietario
           form.save()
           # Actualizar es_cuidador a True
           propietario.es_cuidador = True
           propietario.save()
           messages.success(request,"Registrado como Cuidador!")

           return redirect(to="index")
       
    return render(request,"app_mascotas/cuidador.html",contexto)



@login_required
def perfil(request):
    context = {}
    reseñas_cuidador = []
    cuidador_data = None 
    form_mascota = frmMascota() 
    if request.method == 'POST':
        form_mascota = frmMascota(request.POST, request.FILES)
        if form_mascota.is_valid():
            nueva_mascota = form_mascota.save(commit=False)
            nueva_mascota.propietario = request.user  # Asigna el propietario de la mascota
            nueva_mascota.save()
            messages.success(request, 'Mascota agregada con éxito.')
            return redirect('perfil')
    else:
        form_mascota = frmMascota()
    
    # Obtén todas las mascotas del usuario, activas o no
    todas_mascotas_usuario = Mascota.objects.filter(propietario=request.user)
    # Separa las mascotas activas y desactivadas
    mascotas_activas = todas_mascotas_usuario.filter(es_activo=True)
    mascotas_desactivadas = todas_mascotas_usuario.filter(es_activo=False)
    
    check = Propietario.objects.filter(pk=request.user.id)
    if len(check) > 0:
        data = Propietario.objects.get(pk=request.user.id)
        context["data"] = data
        # Verificar si el usuario es también un cuidador
        if data.es_cuidador:
            cuidador_data = Cuidador.objects.filter(propietario=data).first()
            servicios = Servicio.objects.filter(cuidador=cuidador_data)
            servicios_activos = servicios.filter(es_activo=True)
            servicios_desactivados = servicios.filter(es_activo=False)
            context["cuidador_data"] = cuidador_data
            context["servicios_activos"] = servicios_activos
            context["servicios_desactivados"] = servicios_desactivados
            context["cuidador_data"] = cuidador_data
            # Obtener reseñas asociadas al cuidador
            reseñas_cuidador = Resena.objects.filter(cuidador=cuidador_data).order_by('-fecha_creacion')
            # Paginación para las reseñas
            paginator = Paginator(reseñas_cuidador, 3)
            page_number = request.GET.get('page')
            reseñas_paginadas = paginator.get_page(page_number)
            context["reseñas_cuidador"] = reseñas_paginadas
            
            # Verificar si el usuario es también un cuidador
            if cuidador_data:
                if 'cambiar_disponibilidad' in request.POST:
                    if cuidador_data.disponibilidad == 'Disponible':
                        cuidador_data.disponibilidad = 'Ocupado'
                    elif cuidador_data.disponibilidad == 'Ocupado':
                        cuidador_data.disponibilidad = 'En un trabajo'
                    else:
                        cuidador_data.disponibilidad = 'Disponible'
                    cuidador_data.save()
                    messages.success(request, 'Disponibilidad cambiada con éxito.')
            
    else:
        data = None
    context["mascotas_activas"] = mascotas_activas
    context["mascotas_desactivadas"] = mascotas_desactivadas
    context["form_mascota"] = form_mascota
    
    

    return render(request, "app_mascotas/perfil.html", context)


def desactivar_mascota(request, id_mascota):
    mascota = get_object_or_404(Mascota, id_mascota=id_mascota, propietario=request.user)
    mascota.es_activo = False
    mascota.save()
    messages.success(request, 'Mascota desactivada!')
    return redirect('perfil')

def activar_mascota(request, id_mascota):
    mascota = get_object_or_404(Mascota, id_mascota=id_mascota, propietario=request.user)
    mascota.es_activo = True
    mascota.save()
    messages.success(request, 'Mascota activada!')
    return redirect('perfil')


@login_required
def editar_perfil(request,id):
    us = request.user
    print(us)
    user_role = request.session.get('user_role', None)
    form=frmEdit(instance=us)
    contexto={
        "form":form,
        "user_role": user_role,
    }

    if request.method=="POST":
        form=frmEdit(data=request.POST,files=request.FILES,instance=us)
        #form.fields["id"].disabled=False
        if form.is_valid():
            us_buscado=Propietario.objects.get(id=us.id)
            datos_form=form.cleaned_data
            us_buscado.username=datos_form.get("username")
            us_buscado.first_name=datos_form.get("first_name")
            us_buscado.last_name=datos_form.get("last_name")
            us_buscado.email=datos_form.get("email")
            us_buscado.telefono=datos_form.get("telefono")
            us_buscado.direccion=datos_form.get("direccion")
            us_buscado.imagen=datos_form.get("imagen")
            us_buscado.save()
            messages.success(request,"Información Modificada!")
            return redirect(to="perfil")
        contexto["form"]=form
        
    return render(request,"app_mascotas/editar_perfil.html",contexto)

@login_required
def tipo_servicio(request):
    form=frmTipoServicio(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmTipoServicio(data=request.POST,files=request.FILES)
        if form.is_valid():
           tipo_servicio = form.save(commit=False)
           tipo_servicio.save()
           messages.success(request,"Tipo de servicio agregado!")

           return redirect(to="perfil")
       
    return render(request,"app_mascotas/tipo_servicio.html",contexto)

@login_required
def servicio(request):
    form=frmServicio(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmServicio(data=request.POST,files=request.FILES)
        if form.is_valid():
           servicio = form.save(commit=False)
           cuidador = Cuidador.objects.get(propietario=request.user)
           servicio.cuidador_id = cuidador.id_cuidador
           servicio.save()
           messages.success(request,"Servicio Publicado!")

           return redirect(to="index")
       
    return render(request,"app_mascotas/servicio.html",contexto)

def desactivar_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, cuidador__propietario=request.user)
    servicio.es_activo = False
    servicio.save()
    messages.success(request, 'Servicio desactivado!')
    return redirect('perfil')

def activar_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicio, id_servicio=id_servicio, cuidador__propietario=request.user)
    servicio.es_activo = True
    servicio.save()
    messages.success(request, 'Servicio activado!')
    return redirect('perfil')

@login_required
def especie(request):
    form=frmEspecie(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmEspecie(data=request.POST,files=request.FILES)
        if form.is_valid():
           especie = form.save(commit=False)
           especie.save()
           messages.success(request,"Especie de la mascota agregado!")

           return redirect(to="raza")
       
    return render(request,"app_mascotas/especie.html",contexto)


@login_required
def raza(request):
    form=frmRaza(request.POST or None)
    contexto={
        "form":form
    }
    if request.method=="POST":
        form=frmRaza(data=request.POST,files=request.FILES)
        if form.is_valid():
           raza = form.save(commit=False)
           raza.save()
           messages.success(request,"Raza de la mascota agregado!")

           return redirect(to="perfil")
       
    return render(request,"app_mascotas/raza.html",contexto)


def perfil_servicio(request, cuidador_username):
    cuidador = get_object_or_404(Cuidador, propietario__username=cuidador_username)
    servicios = Servicio.objects.filter(cuidador=cuidador)
    propietario = cuidador.propietario
    prestaciones_activas = None
    
    user_id = request.user.id
    prestaciones_activas = DetPrestacion.objects.filter(id_servicio__in=servicios, estado__in=['Activo', 'Finalizado'], id_propietario=user_id)

        
    obtener = obtener_servicios_activos(propietario.id) if propietario else []
    destinatario = Propietario.objects.exclude(pk=request.user.id)
    mascotas_activas = obtener_mascotas_activas(propietario.id) if propietario else []
    user = request.user
    resenas = Resena.objects.filter(cuidador=cuidador).order_by('-fecha_creacion')
    reseña_existente = None
    
    if prestaciones_activas.exists():
        if request.method == 'POST':
            form = frmResena(request.POST)
            if form.is_valid():
                if Resena.objects.filter(cuidador=cuidador, autor=user).exists():
                    reseña_existente = Resena.objects.get(cuidador=cuidador, autor=user)
                    reseña_existente.texto = form.cleaned_data['texto']
                    reseña_existente.calificacion = form.cleaned_data['calificacion']
                    reseña_existente.fecha_creacion = timezone.now()
                    reseña_existente.fue_editada = True
                    reseña_existente.save()
                    messages.success(request, "Reseña actualizada exitosamente.")
                    return redirect('perfil_servicio', cuidador_username=cuidador_username)
                else:
                    nueva_reseña = form.save(commit=False)
                    nueva_reseña.cuidador = cuidador
                    nueva_reseña.autor = request.user
                    nueva_reseña.save()
                    messages.success(request,"Comentario Agregado!")
                    return redirect('perfil_servicio', cuidador_username=cuidador_username)

        else:
            form = frmResena()
            if Resena.objects.filter(cuidador=cuidador, autor=user).exists():
                reseña_existente = Resena.objects.get(cuidador=cuidador, autor=user)
    else:
        form = None
    
    paginator = Paginator(resenas, 3)
    page_number = request.GET.get('page')
    reseñas_paginadas = paginator.get_page(page_number)
    
    contexto = {
        'servicios': servicios,
        'cuidador': cuidador,
        'propietario': propietario,
        'obtener': obtener,
        'mascotas_activas': mascotas_activas,
        'destinatario': destinatario,
        'user': user,
        'resenas': reseñas_paginadas,
        'form': form,
        'reseña_existente': reseña_existente,
    }
    
    return render(request, 'app_mascotas/perfil_servicio.html', contexto)


def cuenta(request, username):
    usuario = get_object_or_404(Propietario, username=username)
    cuidador = None
    if usuario.es_cuidador:
        cuidador = Cuidador.objects.get(propietario=usuario)
        servicios = Servicio.objects.filter(cuidador=cuidador)
        servicios_activos = servicios.filter(es_activo=True)
    else:
        cuidador = None
        servicios_activos = None
    mascotas_activas = obtener_mascotas_activas(usuario.id) if usuario else []
    servicios = Servicio.objects.filter(cuidador__propietario=usuario)
    reseñas = Resena.objects.filter(cuidador__propietario=usuario).order_by('-fecha_creacion')
    paginator = Paginator(reseñas, 3)
    page_number = request.GET.get('page')
    reseñas_paginadas = paginator.get_page(page_number)
    user = request.user
    prestaciones_activas = None
    reseña_existente = None
    user_id = request.user.id
    prestaciones_activas = DetPrestacion.objects.filter(id_servicio__in=servicios, estado__in=['Activo', 'Finalizado'], id_propietario=user_id)
    if prestaciones_activas.exists():
        if request.method == 'POST':
            form = frmResena(request.POST)
            if form.is_valid():
                if Resena.objects.filter(cuidador=cuidador, autor=user).exists():
                    reseña_existente = Resena.objects.get(cuidador=cuidador, autor=user)
                    reseña_existente.texto = form.cleaned_data['texto']
                    reseña_existente.calificacion = form.cleaned_data['calificacion']
                    reseña_existente.fecha_creacion = timezone.now()
                    reseña_existente.fue_editada = True
                    reseña_existente.save()
                    messages.success(request, "Reseña actualizada exitosamente.")
                    return redirect('cuenta', username=username)
                else:
                    nueva_reseña = form.save(commit=False)
                    nueva_reseña.cuidador = cuidador
                    nueva_reseña.autor = request.user
                    nueva_reseña.save()
                    messages.success(request,"Comentario Agregado!")
                    return redirect('cuenta', username=username)

        else:
            form = frmResena()
            if Resena.objects.filter(cuidador=cuidador, autor=user).exists():
                reseña_existente = Resena.objects.get(cuidador=cuidador, autor=user)
    else:
        form = None
    
    contexto = {
        'usuario': usuario,
        'mascotas_activas': mascotas_activas,
        'servicios': servicios_activos,
        'reseñas': reseñas_paginadas,
        'cuidador': cuidador,
        'form': form,
        'reseña_existente': reseña_existente,
        # Otros datos relevantes del usuario
    }

    return render(request, 'app_mascotas/cuenta.html', contexto)

@login_required
def eliminar_resena(request, id):
    resena = get_object_or_404(Resena, id=id)

    # Asegúrate de que solo el autor de la reseña puede eliminarla
    if resena.autor == request.user:
        # Obtén el cuidador asociado a la reseña
        cuidador = resena.cuidador
        # Obtén el servicio asociado al cuidador
        servicio = Servicio.objects.filter(cuidador=cuidador).first()

        if servicio:
            id_servicio = servicio.id_servicio
            resena.delete()
            messages.success(request, "Comentario Eliminado!")
            return redirect('perfil_servicio', id_servicio=id_servicio)
        else:
            # Manejar el caso en que no se encuentre un servicio asociado
            messages.warning(request, "No se encontró un servicio asociado a la reseña.")
            return redirect('perfil_servicio', id_servicio=resena.cuidador.id_cuidador)


@login_required
def eliminar_servicio(request,id):
    v=get_object_or_404(Servicio,pk=id)
    if request.method=="POST":
        v.delete()
        messages.success(request,"Servicio Eliminado!")
        return redirect(to="perfil")
    
    
@login_required
def modificar_servicio(request,id_servicio):
    prod=get_object_or_404(Servicio,pk=id_servicio)
    form=frmServicio(instance=prod)
    #form.fields["id"].disabled=True
    contexto={
        "form":form
    }

    if request.method=="POST":
        form=frmServicio(data=request.POST,files=request.FILES,instance=prod)
        #form.fields["id"].disabled=False
        if form.is_valid():
            search=Servicio.objects.get(pk=prod.id_servicio)
            datos_form=form.cleaned_data
            search.tipo_servicio=datos_form.get("tipo_servicio")
            search.descripcion=datos_form.get("descripcion")
            search.precio=datos_form.get("precio")
            search.save()
            messages.success(request,"Servicio Modificado!")
            return redirect(to="perfil")
        contexto["form"]=form
        
    return render(request,"app_mascotas/mod_servicio.html",contexto)



@login_required
def eliminar_mascota(request,id):
    v=get_object_or_404(Mascota,pk=id)
    if request.method=="POST":
        v.delete()
        messages.success(request,"Mascota Eliminada!")
        return redirect(to="perfil")




@login_required
def modificar_mascota(request,id_mascota):
    prod=get_object_or_404(Mascota,pk=id_mascota)
    form=frmMascota(instance=prod)
    #form.fields["id"].disabled=True
    contexto={
        "form":form
    }

    if request.method=="POST":
        form=frmMascota(data=request.POST,files=request.FILES,instance=prod)
        #form.fields["id"].disabled=False
        if form.is_valid():
            search=Mascota.objects.get(pk=prod.id_mascota)
            datos_form=form.cleaned_data
            search.id_raza=datos_form.get("id_raza")
            search.nombre_mascota=datos_form.get("nombre_mascota")
            search.peso=datos_form.get("peso")
            search.pelaje=datos_form.get("pelaje")
            search.observaciones=datos_form.get("observaciones")
            search.save()
            messages.success(request,"Mascota Modificada!")
            return redirect(to="perfil")
        contexto["form"]=form
        
    return render(request,"app_mascotas/mod_mascota.html",contexto)



def detalle_prestacion(request, id_servicio):
    servicio = Servicio.objects.get(pk=id_servicio)
    user = request.user
    propietario = servicio.cuidador.propietario

    # Verificar si el usuario está autenticado
    if request.user.is_authenticated:
        if request.method == "POST":
            form = frmDetPrestacion(user, servicio.precio, data=request.POST, files=request.FILES)
            if form.is_valid():
                detalle_prestacion = form.save(commit=False)
                form.instance.id_servicio = servicio
                form.instance.id_propietario = request.user  # Propietario actual
                form.instance.id_cuidador = servicio.cuidador
                detalle_prestacion.save()
                messages.success(request, "Servicio solicitado!")
                return redirect(to="prestacion")
        else:
            form = frmDetPrestacion(user, servicio.precio)

        context = {
            "servicio": servicio,
            "form": form,
            "propietario": propietario,
        }

        return render(request, "app_mascotas/detalle_prestacion.html", context)
    else:
        # Si el usuario no está autenticado, redirigir al login
        return redirect(to="login_custom")




@login_required
def prestacion(request):
    default_page = 1
    page = request.GET.get('page', default_page)
    
    # Obtener todas las prestaciones relacionadas con el propietario (cliente)
    prestaciones_cliente = DetPrestacion.objects.filter(id_propietario=request.user).order_by('-fecha_prestacion')
    items_per_page = 3  # Ajusta el número de elementos por página según tus necesidades
    paginator = Paginator(prestaciones_cliente, items_per_page)

    try:
        prestaciones_cliente = paginator.page(page)
    except PageNotAnInteger:
        prestaciones_cliente = paginator.page(default_page)
    except EmptyPage:
        prestaciones_cliente = paginator.page(paginator.num_pages)
    
    if request.method == 'POST':
        # Obtener el ID de la prestación que se quiere cancelar
        prestacion_id = request.POST.get('id')

        # Buscar la prestación
        prestacion = get_object_or_404(DetPrestacion, id=prestacion_id)

        # Verificar que la prestación está pendiente antes de cambiar el estado
        if prestacion.estado == 'Pendiente':
            # Cambiar el estado de la prestación a 'Cancelado'
            prestacion.estado = 'Cancelado'
            prestacion.save()
            # Actualizar la lista de prestaciones después de la cancelación
            prestaciones_cliente = paginator.page(page)
            # Redirigir de vuelta a la página de prestación para que se reflejen los cambios
            return redirect('prestacion')

    return render(request, 'app_mascotas/prestacion.html', {'prestaciones_cliente': prestaciones_cliente})

@login_required
def prestacion_cuidador(request):
    default_page = 1
    page = request.GET.get('page', default_page)
    cuidador = None
    
    try:
        cuidador = Cuidador.objects.get(propietario=request.user)
    except Cuidador.DoesNotExist:
        cuidador = None
    # Obtener todas las prestaciones relacionadas con el cuidador si existe
    prestaciones_cuidador = DetPrestacion.objects.filter(id_cuidador=cuidador).order_by('-fecha_prestacion') if cuidador else []
    
    if request.method == 'POST':
        # Obtener el ID de la prestación que se quiere cambiar
        id = request.POST.get('id')

        # Buscar la prestación
        prestacion = get_object_or_404(DetPrestacion, id=id)

        # Verificar que la prestación está pendiente antes de cambiar el estado
        if prestacion.estado == 'Pendiente':
            # Cambiar el estado de la prestación a 'Activo'
            prestacion.estado = 'Activo'
            prestacion.save()
        elif prestacion.estado == 'Activo':
            # Cambiar el estado de la prestación a 'Finalizado'
            prestacion.estado = 'Finalizado'
            prestacion.save()
    items_per_page = 3  # Ajusta el número de elementos por página según tus necesidades
    paginator = Paginator(prestaciones_cuidador, items_per_page)
    try:
        prestaciones_cuidador = paginator.page(page)
    except PageNotAnInteger:
        prestaciones_cuidador = paginator.page(default_page)
    except EmptyPage:
        prestaciones_cuidador = paginator.page(paginator.num_pages)
    
    context = {
            "cuidador": cuidador,
            "prestaciones_cuidador": prestaciones_cuidador
        }
    return render(request, 'app_mascotas/prestacion_cuidador.html', context)


@login_required
def inbox(request):
    user = request.user
    messages = Mensaje.get_messages(user)
    recipients = Propietario.objects.exclude(pk=request.user.id)
    paginator = Paginator(messages, 8)
    page_number = request.GET.get('page')
    mensajes_paginadas = paginator.get_page(page_number)
    
    contexto = {
        'messages': mensajes_paginadas,
        'recipients': recipients
    }
    return render(request, 'app_mascotas/inbox.html', contexto)




@login_required
def send_message(request, username, det_prestacion):
    if request.method == 'POST':
        body = request.POST.get('body', '')
        
        try:
            recipient = Propietario.objects.get(username=username)
            det_prestacion = DetPrestacion.objects.get(id=det_prestacion)  # Nueva línea para obtener DetPrestacion
            Mensaje.send_message(request.user, recipient, body, det_prestacion)
            # Redirige de nuevo a la página de conversación
            return redirect('conversation', username=username, det_prestacion=det_prestacion.id)
        except Propietario.DoesNotExist:
            return HttpResponseBadRequest("El destinatario no existe.")
        except DetPrestacion.DoesNotExist:
            return HttpResponseBadRequest("La DetPrestacion no existe.")
        except ValueError as e:
            return HttpResponseBadRequest(str(e))
    else:
        recipients = Propietario.objects.exclude(pk=request.user.id)
        return render(request, 'app_mascotas/send_message.html', {'recipients': recipients})




@login_required
def conversation(request, username, det_prestacion=None):
    user = request.user
    active_direct = username
    directs = Mensaje.objects.filter(user=user, recipient__username=username)
    directs = directs.order_by('-date').filter(det_prestacion=det_prestacion) if det_prestacion else directs.order_by('-date')
    directs.update(is_read=True)
    messages = Mensaje.get_messages(user=request.user, det_prestacion=det_prestacion)

    for message in messages:
        if message['user'].username == user.username:
            message['unread'] = 0
    
    # Paginación para los mensajes
    paginator_messages = Paginator(directs, 5)
    page_number_messages = request.GET.get('messagespage')
    messages_data = paginator_messages.get_page(page_number_messages)
    
    context = {
        'directs': messages_data,
        'active_direct': active_direct,
        'messages': messages,
        'det_prestacion': det_prestacion,
    }

    return render(request, 'app_mascotas/conversation.html', context)







@login_required
def editar_cuidador(request,id_cuidador):
    prod=get_object_or_404(Cuidador,pk=id_cuidador)
    form=frmCuidador(instance=prod)
    #form.fields["id"].disabled=True
    contexto={
        "form":form
    }

    if request.method=="POST":
        form=frmCuidador(data=request.POST,files=request.FILES,instance=prod)
        #form.fields["id"].disabled=False
        if form.is_valid():
            search=Cuidador.objects.get(pk=prod.id_cuidador)
            datos_form=form.cleaned_data
            search.especializacion=datos_form.get("especializacion")
            search.experiencia=datos_form.get("experiencia")
            search.save()
            messages.success(request,"Datos del cuidador modificados!")
            return redirect(to="perfil")
        contexto["form"]=form
        
    return render(request,"app_mascotas/editar_cuidador.html",contexto)



def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def obtener_mascotas_activas(propietario_id):
    with connection.cursor() as cursor:
        cursor.callproc('ObtenerMascotasActivasConDetalle', [propietario_id])
        mascotas_activas = dictfetchall(cursor)
    return mascotas_activas

def obtener_servicios_activos(propietario_id):
    with connection.cursor() as cursor:
        cursor.callproc('ObtenerServiciosActivosConDetalle', [propietario_id])
        servicios_activos = dictfetchall(cursor)

    return servicios_activos


def obtener_resenas_por_propietario_cuidador(propietario_id):
    with connection.cursor() as cursor:
        cursor.callproc('ObtenerResenasPorPropietarioCuidador', [propietario_id])
        resenas_por_cuidador = dictfetchall(cursor)

    return resenas_por_cuidador
