from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

from compras.models import CompraCafe
from productores.models import Productor
from usuarios.models import UsuarioRol


# Obtiene el permiso más alto del usuario para el módulo Historial de compras.
# 0 = Sin acceso
# 1 = Solo ver
# 2 = Acceso administrativo
def obtener_permiso_historial_compras(usuario):

    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    for usuario_rol in roles_usuario:
        rol = usuario_rol.rol

        permiso_actual = getattr(rol, 'historial_compras', 0)

        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


@login_required
def lista_historial_compras(request):

    permiso = obtener_permiso_historial_compras(request.user)

    # Si no tiene permiso para historial, no entra.
    if permiso == 0:
        return redirect('dashboard')

    # Si tiene permiso 2, entra como administrador y ve todas las compras.
    es_administrador_historial = permiso >= 2

    productor_usuario = None
    mensaje_error = None

    if es_administrador_historial:

        compras = CompraCafe.objects.select_related(
            'productor',
            'comunidad'
        ).all()

        buscar = request.GET.get('buscar', '').strip()

        if buscar:
            compras = compras.filter(
                Q(productor_nombre_recibo__icontains=buscar) |
                Q(productor__nombre__icontains=buscar) |
                Q(productor__apellido_paterno__icontains=buscar) |
                Q(productor__apellido_materno__icontains=buscar) |
                Q(comunidad_nombre_recibo__icontains=buscar) |
                Q(fecha_compra__icontains=buscar)
            )

    else:
        # Si tiene permiso 1, se asume vista de productor.
        # Solo debe ver sus propias compras.
        productor_usuario = Productor.objects.filter(
            usuario=request.user
        ).first()

        if productor_usuario:
            compras = CompraCafe.objects.select_related(
                'productor',
                'comunidad'
            ).filter(
                productor=productor_usuario
            )
        else:
            compras = CompraCafe.objects.none()
            mensaje_error = 'No se encontró un productor asociado a este usuario.'

        buscar = ''

    # Última compra primero.
    compras = compras.order_by('-fecha_compra', '-fecha_registro')

    # Paginación igual que Comunidades/Productores: 15 por página.
    paginador = Paginator(compras, 15)
    numero_pagina = request.GET.get('page')
    page_obj = paginador.get_page(numero_pagina)

    contexto = {
        'page_obj': page_obj,
        'buscar': buscar,
        'permiso': permiso,
        'es_administrador_historial': es_administrador_historial,
        'productor_usuario': productor_usuario,
        'mensaje_error': mensaje_error,
    }

    return render(request, 'historial/lista_historial_compras.html', contexto)