from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth

from usuarios.models import UsuarioRol
from compras.models import CompraCafe


def obtener_permiso_analisis(usuario):
    permisos = UsuarioRol.objects.filter(
        usuario=usuario
    ).values_list(
        'rol__analisis_predicciones',
        flat=True
    )

    return max(permisos) if permisos else 0


@login_required
def panel_analisis(request):
    permiso = obtener_permiso_analisis(request.user)

    if permiso == 0:
        return redirect('dashboard')

    # 1. Libras acopiadas por mes
    libras_por_mes = (
        CompraCafe.objects
        .annotate(mes=TruncMonth('fecha_compra'))
        .values('mes')
        .annotate(total_libras=Sum('total_libras'))
        .order_by('mes')
    )

    meses_libras = [
        dato['mes'].strftime('%b %Y') for dato in libras_por_mes
    ]

    valores_libras_mes = [
        float(dato['total_libras'] or 0) for dato in libras_por_mes
    ]

    # 2. Libras acopiadas por comunidad
    libras_por_comunidad = (
        CompraCafe.objects
        .values('comunidad__nombre_comunidad')
        .annotate(total_libras=Sum('total_libras'))
        .order_by('-total_libras')[:10]
    )

    comunidades = [
        dato['comunidad__nombre_comunidad'] or 'Sin comunidad'
        for dato in libras_por_comunidad
    ]

    valores_libras_comunidad = [
        float(dato['total_libras'] or 0) for dato in libras_por_comunidad
    ]

    # 3. Productores que más entregaron café
    top_productores = (
        CompraCafe.objects
        .values(
            'productor__nombre',
            'productor__apellido_paterno',
            'productor__apellido_materno'
        )
        .annotate(total_libras=Sum('total_libras'))
        .order_by('-total_libras')[:10]
    )

    productores = []
    valores_productores = []

    for dato in top_productores:
        nombre = dato['productor__nombre'] or ''
        ap_paterno = dato['productor__apellido_paterno'] or ''
        ap_materno = dato['productor__apellido_materno'] or ''

        nombre_completo = f'{nombre} {ap_paterno} {ap_materno}'.strip()
        productores.append(nombre_completo or 'Sin productor')
        valores_productores.append(float(dato['total_libras'] or 0))

    # 4. Total pagado por mes
    pagado_por_mes = (
        CompraCafe.objects
        .annotate(mes=TruncMonth('fecha_compra'))
        .values('mes')
        .annotate(total_pagado=Sum('total_pagado'))
        .order_by('mes')
    )

    meses_pagado = [
        dato['mes'].strftime('%b %Y') for dato in pagado_por_mes
    ]

    valores_pagado_mes = [
        float(dato['total_pagado'] or 0) for dato in pagado_por_mes
    ]

    contexto = {
        'permiso': permiso,

        'meses_libras': meses_libras,
        'valores_libras_mes': valores_libras_mes,

        'comunidades': comunidades,
        'valores_libras_comunidad': valores_libras_comunidad,

        'productores': productores,
        'valores_productores': valores_productores,

        'meses_pagado': meses_pagado,
        'valores_pagado_mes': valores_pagado_mes,
    }

    return render(request, 'analisis/panel_analisis.html', contexto)