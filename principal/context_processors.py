# imrpotamos el modelo de usuarios
from usuarios.models import UsuarioRol


# Esta función enviará los permisos del usuario a todos los html que hagamos
#era: # 0 = Sin acceso
    # 1 = Solo ver
    # 2 = Crear y modificar
def obtener_permisos(request):
    permisos = { # los modulos
        'registrar_compras_cafe': 0,
        'historial_compras': 0,
        'comunidades': 0,
        'productores': 0,
        'registro_ventas_cafe': 0,
        'analisis_predicciones': 0,
        'roles_usuarios': 0,
    }

    # Lista para guardar los nombres de los roles del usuario.
    roles = []
    #buscamos permisos si logeuamos
    if request.user.is_authenticated:

#buscamos todos los roles segun el usuario que inicio sesion
        roles_usuario = UsuarioRol.objects.filter(usuario=request.user)

#guardamos
        roles = [usuario_rol.rol.nombre_rol for usuario_rol in roles_usuario]


        for usuario_rol in roles_usuario:
#obtenemos el rol
            rol = usuario_rol.rol

            #buscamos el rol que tiene por el numero
            for modulo in permisos.keys():


                permiso_actual = getattr(rol, modulo, 0)

                if permiso_actual > permisos[modulo]:
                    permisos[modulo] = permiso_actual

    return {
        'permisos': permisos,
        'roles': roles,
    }