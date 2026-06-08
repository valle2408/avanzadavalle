from django.contrib import admin
from .models import Productor


# Admin del modelo Productor.
# Sirve para ver productores desde Django Admin.
# En el sistema normal, los productores se crearán automáticamente
# desde Registrar compra de café.
@admin.register(Productor)
class ProductorAdmin(admin.ModelAdmin):

    # Columnas que se verán en la lista del admin.
    list_display = (
        'codigo_productor',
        'nombre',
        'apellido_paterno',
        'apellido_materno',
        'comunidad',
        'estado',
        'usuario',
        'fecha_registro',
    )

    # Campos por los que se podrá buscar en el admin.
    search_fields = (
        'codigo_productor',
        'nombre',
        'apellido_paterno',
        'apellido_materno',
    )

    # Filtros laterales del admin.
    list_filter = (
        'estado',
        'comunidad',
    )

    # Campos que no deberían editarse manualmente desde admin.
    readonly_fields = (
        'fecha_registro',
        'fecha_edicion',
    )

    # Orden de visualización.
    ordering = (
        'nombre',
        'apellido_paterno',
    )
