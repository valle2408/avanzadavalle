from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required 

from usuarios.models import UsuarioRol 


def obtener_permiso_analisis(usuario):
    permisos = UsuarioRol.objects.filter(
        usuario=usuario
    ).values_list(
        'rol__analisis_predicciones',
        flat=True
    )

    return max(permisos) if permisos else 0


@login_required
def panel_analisis(request):
    permiso = obtener_permiso_analisis(request.user)

    if permiso == 0:
        return redirect('principal:dashboard')

    contexto = {
        'permiso': permiso,
    }

    return render(request, 'analisis/panel_analisis.html', contexto)
