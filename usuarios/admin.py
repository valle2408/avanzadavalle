from django.contrib import admin # importa el panel adminsitrativo de django
from django.contrib.auth.admin import UserAdmin #importa useradmin para usuario
from .models import Usuario,Rol,UsuarioRol # importa cosas de la carpeta usuariso

@admin.register(Usuario)

class UsuarioAdmin(UserAdmin): # dice en el video que se heredo
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(Rol) # para manejar los roles

class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'registrar_compras_cafe', 'historial_compras', 'comunidades', 'productores', 'registro_ventas_cafe', 'analisis_predicciones', 'roles_usuarios')
    list_filter = ('registrar_compras_cafe', 'historial_compras', 'comunidades', 'productores', 'registro_ventas_cafe', 'analisis_predicciones', 'roles_usuarios')
    search_fields = ('nombre_rol',)

@admin.register(UsuarioRol)

class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('usuario','rol')
    list_filter = ('rol',)
    search_fields = ('usuario__username', 'rol__nombre_rol')
