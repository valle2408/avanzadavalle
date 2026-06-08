from django.contrib import admin
from .models import CompraCafe, DetallePesajeCompra


# Inline para mostrar los pesajes dentro de la compra en Django Admin.
# Así podremos ver cada bolsa/pesaje registrado en una compra.
class DetallePesajeCompraInline(admin.TabularInline):
    model = DetallePesajeCompra
    extra = 0
    readonly_fields = ('cantidad_libras',)


# Admin de CompraCafe.
# Sirve para revisar las compras registradas desde Django Admin.
@admin.register(CompraCafe)
class CompraCafeAdmin(admin.ModelAdmin):

    list_display = (
        'id_compra',
        'fecha_compra',
        'productor_nombre_recibo',
        'comunidad_nombre_recibo',
        'total_libras',
        'precio_compra',
        'total_pagado',
        'creado_por',
    )

    search_fields = (
        'productor_nombre_recibo',
        'comunidad_nombre_recibo',
        'codigo_productor_recibo',
    )

    list_filter = (
        'fecha_compra',
        'comunidad',
    )

    readonly_fields = (
        'total_libras',
        'total_pagado',
        'productor_nombre_recibo',
        'comunidad_nombre_recibo',
        'codigo_productor_recibo',
        'fecha_registro',
    )

    inlines = [
        DetallePesajeCompraInline,
    ]

    ordering = (
        '-fecha_compra',
        '-fecha_registro',
    )


# Admin de DetallePesajeCompra.
# Permite revisar los pesajes de manera independiente si fuera necesario.
@admin.register(DetallePesajeCompra)
class DetallePesajeCompraAdmin(admin.ModelAdmin):

    list_display = (
        'id_detalle_pesaje',
        'compra',
        'cantidad_libras',
    )

    search_fields = (
        'compra__productor_nombre_recibo',
    )
