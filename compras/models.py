from django.db import models
from django.conf import settings
from decimal import Decimal # para datos decimales
from comunidades.models import Comunidad # para traer datos de la comunidad
from productores.models import Productor # datos del productor


#modelo CompraCafe
class CompraCafe(models.Model):

    id_compra = models.AutoField(primary_key=True) # llave primaria
#preteccion para no borrar productores
    productor = models.ForeignKey(
        Productor,
        on_delete=models.PROTECT,
        related_name='compras_cafe',
        verbose_name='Productor'
    )
# relacionamos con comunidad nuevamente
    comunidad = models.ForeignKey(
        Comunidad,
        on_delete=models.PROTECT,
        related_name='compras_cafe',
        verbose_name='Comunidad'
    )
#fecha compra autimatica
    fecha_compra = models.DateField(
        verbose_name='Fecha de compra'
    )
# precio pagado por libras y datos tipo decimalfield para decimales
    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio de compra por libra'
    )
#total de libras compras igual con decimalfield para decimales
    total_libras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total de libras'
    )
#total pagado
    total_pagado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Total pagado'
    )

 # datos congelados para el recibo
    productor_nombre_recibo = models.CharField(
        max_length=300,
        verbose_name='Productor en recibo'
    )

    comunidad_nombre_recibo = models.CharField(
        max_length=150,
        verbose_name='Comunidad en recibo'
    )

    codigo_productor_recibo = models.CharField(
        max_length=20,
        verbose_name='Código del productor en recibo'
    )

# el suuario que registro la compra
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras_cafe_creadas',
        verbose_name='Creado por'
    )

  #fecha y hora en que se registro la compra en el sistema
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    class Meta:
        db_table = 'compras_cafe'
        verbose_name = 'Compra de café'
        verbose_name_plural = 'Compras de café'
        ordering = ['-fecha_compra', '-fecha_registro']

    def __str__(self):
        return f"Compra {self.id_compra} - {self.productor_nombre_recibo}"

# calcular decimales auxiliar
    def calcular_total_pagado(self):
        total = self.total_libras * self.precio_compra
        return total.quantize(Decimal('0.01'))


# Modelo DetallePesajeCompra
class DetallePesajeCompra(models.Model):
    id_detalle_pesaje = models.AutoField(primary_key=True) # llave primaria

# compra a la que pertenece este pesaje
    compra = models.ForeignKey(
        CompraCafe,
        on_delete=models.CASCADE,
        related_name='pesajes',
        verbose_name='Compra'
    )
#cantidad de libras de este pesaje especifico
    cantidad_libras = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Cantidad de libras'
    )
    class Meta:
        db_table = 'detalles_pesaje_compra'
        verbose_name = 'Detalle de pesaje'
        verbose_name_plural = 'Detalles de pesajes'

    def __str__(self):
        return f"{self.cantidad_libras} lb"
