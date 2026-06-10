from django.contrib import admin
from .models import VentaCafe


@admin.register(VentaCafe)
class VentaCafeAdmin(admin.ModelAdmin):
    list_display = (
        'numero_ingreso',
        'fecha_venta',
        'empresa_compradora',
        'tipo_cafe',
        'cantidad_sacos',
        'peso_total_kg',
        'registrado_por',
    )

    search_fields = (
        'numero_ingreso',
        'empresa_compradora',
        'tipo_cafe',
    )

    list_filter = (
        'tipo_cafe',
        'fecha_venta',
    )

    readonly_fields = (
        'fecha_registro',
    )
