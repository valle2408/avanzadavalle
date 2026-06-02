from django.db import models  # CREA MODELOS PARA LA BD
from django.contrib.auth.models import AbstractUser # EL ABSTRACT TRAE UNA CLASE DE DJANGO PARA USAR
class Usuario(AbstractUser): # CREAMOS LA CLASE USUARIO
    usuario_id = models.AutoField(primary_key=True) #CAMPO USUARIO ID, ES NUMEROS AUTOMATICOS Y ES LLAVE PRIMARIA
    #username = models.CharField(max_length=150, unique=True) #CAMPO USERNAME Y NO SE PUEDE REPETIR
    #password = models.CharField(max_length=128) # PASSWORD 
    USERNAME_FIELD = 'username' # CAMPO PARA INICIAR SESION
    class Meta: # CONFIGURACIONES EXTRAS en la bd
        db_table = 'usuarios' # nombre de la tabla
        verbose_name = 'Usuario' # definimos en sigular el modelo dentro del panel de django
        verbose_name_plural = 'Usuarios' # define como se mostrara en plural en django
        
class Rol(models.Model): # representa los roles del sistema
    OPCIONES_PERMISO = [
        (0, 'Sin acceso'),
        (1, 'Solo Ver'),
        (2, 'Crear y Modificar'),
    ]
    nombre_rol = models.CharField(max_length= 50, primary_key= True) # creamos el campo rol 
    # mis modulos en el dashboard
    registrar_compras_cafe = models.IntegerField(choices = OPCIONES_PERMISO,default= 0)
    historial_compras = models.IntegerField(choices = OPCIONES_PERMISO,default= 0)
    comunidades = models.IntegerField(choices= OPCIONES_PERMISO,default= 0)
    productores = models.IntegerField(choices= OPCIONES_PERMISO, default= 0)
    registro_ventas_cafe = models.IntegerField(choices= OPCIONES_PERMISO,default= 0)
    analisis_predicciones = models.IntegerField(choices= OPCIONES_PERMISO,default= 0)
    roles_usuarios = models.IntegerField(choices= OPCIONES_PERMISO,default= 0)


    class Meta: # configuracion extra para rol
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    def __str__(self): # define como se mostrara cuando tenga su rol
        return self.nombre_rol # puede ser el nombre del rol que pongamos
    
class UsuarioRol(models.Model): # relaciona el rol con el usuario que vamos a crear
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE) # crea una relaciona con la tabla  usuario 
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE) # tambien crea una relacion con el rol

    #cambios extras
    class Meta:
        db_table = 'usuario_rol'
        verbose_name = 'Usuario Rol'
        verbose_name_plural = 'Usuarios Roles'
        unique_together = ('usuario', 'rol') # EVITA QUE SE CREEN DOS
    def __str__(self):
        return f"{self.usuario.username} - {self.rol.nombre_rol}"

