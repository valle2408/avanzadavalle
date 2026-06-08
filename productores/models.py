from django.db import models
from django.conf import settings

from comunidades.models import Comunidad


# Modelo del productor, es el usuario que vende cafe a la empresa
# estajunto con comunidad y usuario
class Productor(models.Model):

    # ponemos inactivo e activo por un usurio no elimina por que tendra historial. mejor inactivarlo
    OPCIONES_ESTADO = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ]

    id_productor = models.AutoField(primary_key=True) #llave primaria

    # Código único del productor, tambien servira para wl login dl productor
    codigo_productor = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código del productor'
    )

    #nombre del productor.
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre'
    )

    #apellido paterno 
    apellido_paterno = models.CharField(
        max_length=100,
        verbose_name='Apellido paterno'
    )

    # apellido materno
    apellido_materno = models.CharField(
        max_length=100,
        blank=True, # no pasa nada si se queda vacio
        verbose_name='Apellido materno'
    )

    # la relacionamos con comunidad
    comunidad = models.ForeignKey(
        Comunidad,
        on_delete=models.PROTECT,
        related_name='productores',
        verbose_name='Comunidad'
    )

    # relaciónamos con usuario y aremos la pruebaas
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productor',
        verbose_name='Usuario de acceso'
    )

    # estado del productor
    estado = models.CharField(
        max_length=20,
        choices=OPCIONES_ESTADO,
        default='Activo',
        verbose_name='Estado'
    )

    # Usuario o admnistrador que creo al productor
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productores_creados',
        verbose_name='Creado por'
    )

    # echa de registro del productor.para la primera compra
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    # usuario o admnistrador que editó el productor por última vez.
    editado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='productores_editados',
        verbose_name='Editado por'
    )

    # fecha de última edición.
    fecha_edicion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de edición'
    )

    class Meta:
        db_table = 'productores'
        verbose_name = 'Productor'
        verbose_name_plural = 'Productores'

    # Devuelve el nombre completo del productor y no por partes
    def __str__(self):
        return self.nombre_completo()

    # para nombre completo
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}".strip()