from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Q, Value, DecimalField
from django.db.models.functions import Coalesce

from .models import Productor
from .forms import FormularioProductor

from usuarios.models import UsuarioRol
from compras.models import CompraCafe


# Función para obtener el permiso del usuario en el módulo Productores.
# 0 = Sin acceso
# 1 = Solo ver
# 2 = Crear y modificar
def obtener_permiso_productores(usuario):

    # Buscamos los roles del usuario logueado.
    roles_usuario = UsuarioRol.objects.filter(usuario=usuario)

    permiso_maximo = 0

    # Recorremos los roles para encontrar el permiso más alto.
    for usuario_rol in roles_usuario:

        rol = usuario_rol.rol

        # Obtenemos el permiso del módulo productores.
        permiso_actual = getattr(rol, 'productores', 0)

        if permiso_actual > permiso_maximo:
            permiso_maximo = permiso_actual

    return permiso_maximo


# Vista para listar productores.
@login_required
def lista_productores(request):

    permiso = obtener_permiso_productores(request.user)

    # Si no tiene acceso, vuelve al dashboard.
    if permiso == 0:
        return redirect('dashboard')

    # Obtenemos todos los productores con su comunidad y usuario.
    # Además calculamos:
    # - total_compras_real: cantidad de compras registradas
    # - total_libras_real: suma de libras entregadas
    productores = Productor.objects.select_related(
        'comunidad',
        'usuario'
    ).annotate(
        total_compras_real=Count('compras_cafe'),
        total_libras_real=Coalesce(
            Sum('compras_cafe__total_libras'),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by(
        'nombre',
        'apellido_paterno'
    )

    # Buscador por nombre, apellidos, código o comunidad.
    buscar = request.GET.get('buscar')

    if buscar:
        productores = productores.filter(
            Q(nombre__icontains=buscar) |
            Q(apellido_paterno__icontains=buscar) |
            Q(apellido_materno__icontains=buscar) |
            Q(codigo_productor__icontains=buscar) |
            Q(comunidad__nombre_comunidad__icontains=buscar)
        )

    # Paginación: mostramos 15 productores por página.
    paginator = Paginator(productores, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
    }

    return render(request, 'productores/lista_productores.html', contexto)


# Vista para ver el detalle de un productor.
@login_required
def detalle_productor(request, pk):

    permiso = obtener_permiso_productores(request.user)

    # Si no tiene acceso, vuelve al dashboard.
    if permiso == 0:
        return redirect('dashboard')

    productor = get_object_or_404(
        Productor.objects.select_related('comunidad', 'usuario'),
        pk=pk
    )

    # Compras realizadas a este productor.
    compras = CompraCafe.objects.filter(
        productor=productor
    ).order_by(
        '-fecha_compra',
        '-fecha_registro'
    )

    # Buscador por fecha en el detalle.
    fecha = request.GET.get('fecha')

    if fecha:
        compras = compras.filter(fecha_compra=fecha)

    # Totales reales desde CompraCafe.
    resumen = CompraCafe.objects.filter(
        productor=productor
    ).aggregate(
        total_compras=Count('id_compra'),
        total_libras=Coalesce(
            Sum('total_libras'),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        total_pagado=Coalesce(
            Sum('total_pagado'),
            Value(Decimal('0.00')),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )

    total_compras = resumen['total_compras']
    total_libras = resumen['total_libras']
    total_pagado = resumen['total_pagado']

    # Última compra real.
    ultima_compra = CompraCafe.objects.filter(
        productor=productor
    ).order_by(
        '-fecha_compra',
        '-fecha_registro'
    ).first()

    contexto = {
        'productor': productor,
        'compras': compras,
        'total_compras': total_compras,
        'total_libras': total_libras,
        'total_pagado': total_pagado,
        'ultima_compra': ultima_compra,
    }

    return render(request, 'productores/detalle_productor.html', contexto)


# Vista para editar datos básicos del productor.
# Solo se podrán editar nombre, apellidos, comunidad y estado.
@login_required
def editar_productor(request, pk):

    permiso = obtener_permiso_productores(request.user)

    # Solo usuarios con permiso 2 pueden editar.
    if permiso < 2:
        return redirect('productores:detalle_productor', pk=pk)

    productor = get_object_or_404(Productor, pk=pk)

    if request.method == 'POST':
        form = FormularioProductor(request.POST, instance=productor)

        if form.is_valid():
            productor = form.save(commit=False)

            # Guardamos quién editó al productor.
            productor.editado_por = request.user

            productor.save()

            # Mensaje propio de Productores usando parámetro en la URL.
            # Así evitamos que el mensaje se arrastre a otros módulos.
            return redirect(f'/productores/{productor.pk}/detalle/?editado=1')

    else:
        form = FormularioProductor(instance=productor)

    contexto = {
        'form': form,
        'productor': productor,
    }

    return render(request, 'productores/formulario_productor.html', contexto)
