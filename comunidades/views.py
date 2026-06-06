from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required # para el login , osea si esta logeuado permitir realizar acciones de aqui
from django.contrib import messages # mpara mensajes

from .models import Comunidad # importamos los dartos de comunidad
from .forms import FormularioComunidad # del dormulario de comunidad

from usuarios.models import UsuarioRol # y datos de los usuarios para utilizarlo en la logica

#era
# 0 sin acceso
# 1 solo ver
# 2 crear y modificar en base a eso aremos la logica de lo demas mas el autenticado para eso
def obtener_permiso_comunidades(usuario):

    #buscmos los roles
    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    # Roles del usuario
    for usuario_rol in roles_usuario:

        # Obtenemos el rol
        rol = usuario_rol.rol
        permiso_actual = getattr(rol, 'comunidades', 0)
        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# listar comunidades y buscar por ombre
@login_required # seguridad y login requeido para entrar
def lista_comunidades(request):

    permiso = obtener_permiso_comunidades(request.user)
    if permiso == 0:
        return redirect('dashboard') # si no esta permitido vuelve al dashboard osea atras
    
    comunidades = Comunidad.objects.all().order_by('nombre_comunidad')# listamos las comunidades

    nombre_comunidad = request.GET.get('nombre_comunidad') # buscador busca

    if nombre_comunidad:
        comunidades = comunidades.filter(nombre_comunidad__icontains=nombre_comunidad) #filtra

    contexto = {
        'comunidades': comunidades,
        'permiso': permiso,
    }

    return render(request, 'comunidades/lista_comunidades.html', contexto)


# para crar
@login_required # login
def crear_comunidad(request):

    permiso = obtener_permiso_comunidades(request.user)

    # acceso mas de 2 para crear y modfiicar
    if permiso < 2:
        return redirect('comunidades:lista_comunidades')

    if request.method == 'POST':
        form = FormularioComunidad(request.POST)

        if form.is_valid():
            comunidad = form.save(commit=False)

            # Guardamos con el usuari que creo osea user
            comunidad.creado_por = request.user
            comunidad.save()

            messages.success(request, 'Comunidad creada correctamente.')
            return redirect('comunidades:lista_comunidades')

    else:
        form = FormularioComunidad()

    contexto = {
        'form': form,
    }

    return render(request, 'comunidades/formulario_comunidad.html', contexto)


# para editar
@login_required # login , seguridad requerida es bueno esto
def editar_comunidad(request, pk):

    permiso = obtener_permiso_comunidades(request.user)

# acceso mas de dos para eidtar
    if permiso < 2:
        return redirect('comunidades:lista_comunidades')

    # Buscamos la comundad
    comunidad = get_object_or_404(Comunidad, pk=pk)

    if request.method == 'POST':
        form = FormularioComunidad(request.POST, instance=comunidad)

        if form.is_valid():
            comunidad = form.save(commit=False)

            # Guardamos la edicion por user
            comunidad.editado_por = request.user
            comunidad.save()

            messages.success(request, 'Comunidad editada correctamente.')
            return redirect('comunidades:lista_comunidades')

    else:
        form = FormularioComunidad(instance=comunidad)

    contexto = {
        'form': form,
        'comunidad': comunidad,
    }

    return render(request, 'comunidades/formulario_comunidad.html', contexto)


#para eliminar pero comentaremos si es necesario opcional
@login_required # login
def eliminar_comunidad(request, pk):

    permiso = obtener_permiso_comunidades(request.user)

# mas de 2 para eliminar 
    if permiso < 2:
        return redirect('comunidades:lista_comunidades')

    comunidad = get_object_or_404(Comunidad, pk=pk)
    if request.method == 'POST':
        comunidad.delete()

        messages.success(request, 'Comunidad eliminada correctamente.')
        return redirect('comunidades:lista_comunidades')

    return redirect('comunidades:lista_comunidades')
