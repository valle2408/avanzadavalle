from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Productor
from .forms import FormularioProductor

from usuarios.models import UsuarioRol


#los permiso del usuario 
# 0 = Sin acceso
# 1 = Solo ver
# 2 = Crear y modificar
def obtener_permiso_productores(usuario):

    # buscamos los roles 
    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    # recorremos los roles
    for usuario_rol in roles_usuario:

        rol = usuario_rol.rol

        # obtenemos el permiso del módulo productores.
        permiso_actual = getattr(rol, 'productores', 0)

        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# logica para listar productores
@login_required # tiene que estar logeuado
def lista_productores(request):

    permiso = obtener_permiso_productores(request.user)

    # si no tiene acceso, vuelve al dashboard
    if permiso == 0:
        return redirect('dashboard')

    # relacion comunidad y obtenemos eso
    productores = Productor.objects.select_related('comunidad', 'usuario').all().order_by('nombre', 'apellido_paterno')

    # Buscador por nombre o apellidos
    buscar = request.GET.get('buscar')

    if buscar:
        productores = productores.filter(
            nombre__icontains=buscar
        ) | productores.filter(
            apellido_paterno__icontains=buscar
        ) | productores.filter(
            apellido_materno__icontains=buscar
        )

    # Paginacion mostramos 15 productores por página o podemos cambiar desdde aqui
    paginator = Paginator(productores, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
    }

    return render(request, 'productores/lista_productores.html', contexto)


# logica para ver el detalle del productor osea la accion ver
@login_required
def detalle_productor(request, pk):

    permiso = obtener_permiso_productores(request.user)

    # si no tiene acceso, vuelve al dashboard.
    if permiso == 0:
        return redirect('dashboard')

    productor = get_object_or_404(
        Productor.objects.select_related('comunidad', 'usuario'),
        pk=pk
    )

    # estos datos seran calculados desde el modulo compras en el futuro.
    # por ahora se dejan en 0 o Sin compras.
    total_compras = 0
    total_libras = 0
    total_pagado = 0
    ultima_compra = None

    contexto = {
        'productor': productor,
        'total_compras': total_compras,
        'total_libras': total_libras,
        'total_pagado': total_pagado,
        'ultima_compra': ultima_compra,
    }

    return render(request, 'productores/detalle_productor.html', contexto)


# Vista para editar datos del productor nonbres y comunidad, lo demas dejarlo asi
@login_required
def editar_productor(request, pk):

    permiso = obtener_permiso_productores(request.user)

    # Solo usuarios con permiso 2 pueden editar, osea los roles
    if permiso < 2:
        return redirect('productores:detalle_productor', pk=pk)

    productor = get_object_or_404(Productor, pk=pk)

    if request.method == 'POST':
        form = FormularioProductor(request.POST, instance=productor)

        if form.is_valid():
            productor = form.save(commit=False)

            # guardamos
            productor.editado_por = request.user

            productor.save()

            messages.success(request, 'Productor editado correctamente.')
            return redirect('productores:detalle_productor', pk=productor.pk)

    else:
        form = FormularioProductor(instance=productor)

    contexto = {
        'form': form,
        'productor': productor,
    }

    return render(request, 'productores/formulario_productor.html', contexto)
