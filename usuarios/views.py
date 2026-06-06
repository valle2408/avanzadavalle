from django.shortcuts import render, redirect # para el redireccionamiento
from django.contrib.auth import authenticate, login, logout #para la verificacion , para el login y cierre

# un midwillers para que oblique al usario esta autenticado
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import FormularioLogin # DE LA CARPETA QUE CREAMOS IMPORTAMOS SU CLASE
from .models import UsuarioRol, Rol

#FUNCION DEL LOGIN
def iniciar_sesion(request):

    # si el usuario ya inicio sesion se manda directamente el dashboatf
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # si usuario envio el formulario post
    if request.method == 'POST':
        form = FormularioLogin(request, data = request.POST)


#varifica si los datos del formulario son validos
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Usuario o Contraseña Incorrectos')
    else:
        form = FormularioLogin()
    return render(request, 'usuarios/login.html', {'form': form})
#FUNCIONA DE LOGOUT
@login_required
def cerrar_sesion(request):
    logout(request)
    messages.success(request, 'Cierre de Sesion exitoso')
    return redirect ('login')
