import random
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q

from usuarios.models import Rol, UsuarioRol
from productores.models import Productor


# Obtiene el permiso más alto del usuario para Roles y usuarios.
# 0 = Sin acceso
# 1 = Solo ver
# 2 = Crear y modificar
def obtener_permiso_roles_usuarios(usuario):

    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    for usuario_rol in roles_usuario:
        rol = usuario_rol.rol

        permiso_actual = getattr(rol, 'roles_usuarios', 0)

        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# Genera contraseña temporal corta.
# Ejemplo: av4827k
def generar_password_temporal():

    letras = string.ascii_lowercase
    numeros = string.digits

    return (
        "av"
        + "".join(random.choices(numeros, k=4))
        + random.choice(letras)
    )


# Obtiene el primer rol asignado al usuario.
def obtener_rol_actual(usuario):

    usuario_rol = UsuarioRol.objects.filter(usuario=usuario).first()

    if usuario_rol:
        return usuario_rol.rol

    return None


# Lista principal de usuarios y roles.
@login_required
def lista_usuarios(request):

    permiso = obtener_permiso_roles_usuarios(request.user)

    # Solo administrador con permiso 2 puede entrar al módulo.
    if permiso < 2:
        return redirect('dashboard')

    Usuario = get_user_model()

    usuarios = Usuario.objects.all().order_by('username')

    buscar = request.GET.get('buscar', '').strip()

    if buscar:
        usuarios = usuarios.filter(
            Q(username__icontains=buscar) |
            Q(first_name__icontains=buscar) |
            Q(last_name__icontains=buscar)
        )

    paginador = Paginator(usuarios, 15)
    numero_pagina = request.GET.get('page')
    page_obj = paginador.get_page(numero_pagina)

    roles_disponibles = Rol.objects.filter(
        nombre_rol__in=['Administrador', 'Productor']
    ).order_by('nombre_rol')

    usuarios_mostrados = []

    for usuario in page_obj:

        productor = Productor.objects.filter(usuario=usuario).select_related('comunidad').first()
        rol_actual = obtener_rol_actual(usuario)

        if productor:
            nombre_completo = productor.nombre_completo()
            comunidad = productor.comunidad.nombre_comunidad
            estado = productor.estado
        else:
            nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()

            if not nombre_completo:
                nombre_completo = usuario.username

            comunidad = "—"
            estado = "Activo" if usuario.is_active else "Inactivo"

        usuarios_mostrados.append({
            'usuario': usuario,
            'productor': productor,
            'nombre_completo': nombre_completo,
            'comunidad': comunidad,
            'rol_actual': rol_actual,
            'estado': estado,
        })

    contexto = {
        'page_obj': page_obj,
        'usuarios_mostrados': usuarios_mostrados,
        'roles_disponibles': roles_disponibles,
        'buscar': buscar,
    }

    return render(request, 'roles/lista_usuarios.html', contexto)


# Cambia el rol del usuario.
@login_required
def cambiar_rol_usuario(request, pk):

    permiso = obtener_permiso_roles_usuarios(request.user)

    if permiso < 2:
        return redirect('dashboard')

    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':

        nuevo_rol_nombre = request.POST.get('rol')

        nuevo_rol = get_object_or_404(Rol, nombre_rol=nuevo_rol_nombre)

        # Para este sistema manejaremos un rol principal por usuario.
        # Eliminamos roles anteriores y asignamos el nuevo.
        UsuarioRol.objects.filter(usuario=usuario).delete()

        UsuarioRol.objects.create(
            usuario=usuario,
            rol=nuevo_rol
        )

        return redirect('/roles/?rol_cambiado=1')

    return redirect('roles:lista_usuarios')


# Cambia el estado Activo/Inactivo del usuario.
@login_required
def cambiar_estado_usuario(request, pk):

    permiso = obtener_permiso_roles_usuarios(request.user)

    if permiso < 2:
        return redirect('dashboard')

    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':

        nuevo_estado = request.POST.get('estado')

        if nuevo_estado == 'Activo':
            usuario.is_active = True
        else:
            usuario.is_active = False

        usuario.save()

        productor = Productor.objects.filter(usuario=usuario).first()

        if productor:
            productor.estado = nuevo_estado
            productor.editado_por = request.user
            productor.save()

        return redirect('/roles/?estado_cambiado=1')

    return redirect('roles:lista_usuarios')


# Pantalla para resetear la contraseña del usuario.
@login_required
def resetear_password_usuario(request, pk):

    permiso = obtener_permiso_roles_usuarios(request.user)

    if permiso < 2:
        return redirect('dashboard')

    Usuario = get_user_model()
    usuario = get_object_or_404(Usuario, pk=pk)

    productor = Productor.objects.filter(usuario=usuario).select_related('comunidad').first()
    rol_actual = obtener_rol_actual(usuario)

    if productor:
        nombre_completo = productor.nombre_completo()
        comunidad = productor.comunidad.nombre_comunidad
        estado = productor.estado
    else:
        nombre_completo = f"{usuario.first_name} {usuario.last_name}".strip()

        if not nombre_completo:
            nombre_completo = usuario.username

        comunidad = "—"
        estado = "Activo" if usuario.is_active else "Inactivo"

    nueva_password = None

    if request.method == 'POST':

        nueva_password = generar_password_temporal()

        usuario.set_password(nueva_password)
        usuario.save()

    contexto = {
        'usuario_objetivo': usuario,
        'productor': productor,
        'nombre_completo': nombre_completo,
        'comunidad': comunidad,
        'rol_actual': rol_actual,
        'estado': estado,
        'nueva_password': nueva_password,
    }

    return render(request, 'roles/resetear_password.html', contexto)