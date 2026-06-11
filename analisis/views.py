
import csv
import json
from pathlib import Path
from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.conf import settings

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


def obtener_predicciones_hasta_diciembre():
    hoy = date.today()
    gestion_actual = hoy.year
    mes_actual = hoy.month

    nombres_meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    ruta_csv = (
        Path(settings.BASE_DIR)
        / "modeloia"
        / "predicciones_futuras"
        / "datasets"
        / "predicciones_futuras_2021_2026.csv"
    )

    predicciones = []

    if ruta_csv.exists():
        with open(ruta_csv, mode="r", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)

            for fila in lector:
                gestion = int(float(fila["gestion"]))
                mes = int(float(fila["mes"]))
                prediccion_libras = float(fila["prediccion_libras"])

                # Solo mostrar desde el mes actual hasta diciembre
                # de la gestión actual.
                if gestion == gestion_actual and mes >= mes_actual and mes <= 12:
                    predicciones.append({
                        "periodo": fila["periodo"],
                        "gestion": gestion,
                        "mes": mes,
                        "nombre_mes": nombres_meses.get(mes, str(mes)),
                        "prediccion_libras": round(prediccion_libras, 2),
                        "nivel_acopio_estimado": fila["nivel_acopio_estimado"],
                        "observacion": fila["observacion"],
                    })

    total_estimado = 0
    promedio_estimado = 0
    mes_mayor = None
    mes_menor = None

    if predicciones:
        total_estimado = sum(item["prediccion_libras"] for item in predicciones)
        promedio_estimado = total_estimado / len(predicciones)
        mes_mayor = max(predicciones, key=lambda item: item["prediccion_libras"])
        mes_menor = min(predicciones, key=lambda item: item["prediccion_libras"])

    datos_grafico_prediccion = {
        "meses": [item["nombre_mes"] for item in predicciones],
        "libras": [item["prediccion_libras"] for item in predicciones],
    }

    return {
        "gestion_actual": gestion_actual,
        "mes_actual": nombres_meses.get(mes_actual, str(mes_actual)),
        "predicciones_hasta_diciembre": predicciones,
        "total_prediccion_hasta_diciembre": round(total_estimado, 2),
        "promedio_prediccion_hasta_diciembre": round(promedio_estimado, 2),
        "mes_mayor_prediccion": mes_mayor,
        "mes_menor_prediccion": mes_menor,
        "datos_grafico_prediccion": json.dumps(datos_grafico_prediccion),
        "existe_archivo_predicciones": ruta_csv.exists(),
    }


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

    # 5. Predicciones futuras desde el mes actual hasta diciembre
    datos_predicciones = obtener_predicciones_hasta_diciembre()

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

    contexto.update(datos_predicciones)

    return render(request, 'analisis/panel_analisis.html', contexto)

