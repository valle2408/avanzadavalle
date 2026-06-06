from django.db import models
from django.conf import settings

# creamos la tabla o el modelo de comunidades 

class Comunidad(models.Model): # modelo comunidad 

    OPCIONES_ESTADO = [ # servira para poner activo e inactivo pero nunca delete de nuestro sistmas la comunidad
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ]

    id_comunidad = models.AutoField(primary_key=True) ## llave primaria
    nombre_comunidad = models.CharField(max_length=100, unique=True, verbose_name='Nombre de la comunidad') # nombre de la comunidad
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default='Activo', verbose_name='Estado') # estado de la comunidad

    creado_por = models.ForeignKey( # quien lo creo 
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='comunidades_creadas',
        verbose_name='Creado por'
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación') # fecha de la crecion

    editado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comunidades_editadas',
        verbose_name='Editado por'
    )

    fecha_edicion = models.DateTimeField(auto_now=True, verbose_name='Fecha de edición') # la fecha de la edidion

    class Meta:
        db_table = 'comunidades' # nombre de la tabla 
        verbose_name = 'Comunidad'
        verbose_name_plural = 'Comunidades'

    def __str__(self): # para django admin y para nosotros tambien en modo texto
        return self.nombre_comunidad