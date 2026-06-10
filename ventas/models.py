from django.conf import settings
from django.db import models


class VentaCafe(models.Model):

    TIPOS_CAFE = [
        ('Cafe pergamino', 'Café pergamino'),
        ('Cafe oro', 'Café oro'),
        ('Cafe miel / honey', 'Café miel / honey'),
    ]

    id_venta = models.AutoField(primary_key=True)

    numero_ingreso = models.CharField(
        max_length=50,
        unique=True
    )

    fecha_venta = models.DateField()

    empresa_compradora = models.CharField(
        max_length=150
    )

    tipo_cafe = models.CharField(
        max_length=30,
        choices=TIPOS_CAFE
    )

    procedencia = models.CharField(
        max_length=100,
        default='Irupana'
    )

    proveedor = models.CharField(
        max_length=100,
        default='La Avanzada'
    )

    cantidad_sacos = models.PositiveIntegerField()

    peso_total_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_registradas'
    )

    editado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas_editadas'
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ventas_cafe'
        ordering = ['-fecha_venta', '-fecha_registro']
        verbose_name = 'Venta de café'
        verbose_name_plural = 'Ventas de café'

    def __str__(self):
        return f"{self.numero_ingreso} - {self.empresa_compradora}"
