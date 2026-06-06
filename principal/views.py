from django.shortcuts import render
from django.contrib.auth.decorators import login_required ## llamamos con decoradores
from usuarios.models import UsuarioRol

#inicio de sesion requerida para esto
@login_required 
def dashboard(request):


    roles_usuario = UsuarioRol.objects.filter(usuario=request.user) # buscael rol que usuario inicio sesion
    permisos = {
        'registrar_compras_cafe': 0,
        'historial_compras': 0,
        'comunidades': 0,
        'productores': 0,
        'registro_ventas_cafe': 0,
        'analisis_predicciones': 0,
        'roles_usuarios': 0,
    }
    
    #recorremos todos los roles que tiene el usuario
    for usuario_rol in roles_usuario:

        #obtenemos el rol que tiene
        rol = usuario_rol.rol

        # recorremos los permisos por modulos 
        for modulo in permisos.keys():

            #obtenemos el permiso
            permiso_actual = getattr(rol,modulo)

            #si el rol es mayor al permiso lo reemplazamos
            if permiso_actual > permisos[modulo]:
                permisos[modulo] = permiso_actual
    
    #dato que enviamos al html de dashboard
    context = {
        'usuario': request.user,
        'permisos': permisos,
        'roles': [ur.rol.nombre_rol for ur in roles_usuario],
        
    }
    return render(request, 'principal/dashboard.html', context)