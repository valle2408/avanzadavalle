# este formulario recibe los datos desde la pagina html que crearemos
"""
models.py  = tablas de la base de datos
forms.py   = formularios para capturar datos
views.py   = lógica que procesa esos datos
html       = parte visual
"""

from django import forms # las herramientas de djanfgo las expotamos
from django.contrib.auth.forms import AuthenticationForm # para el login y el formulario
from .models import Usuario # importamos el Usuario en models.py en usuarios

class FormularioLogin(AuthenticationForm): # creamos el formulario personalizado
    username = forms.CharField( #campo interno pero visible
        label= 'Usuario',
        widget= forms.TextInput(attrs={
            'class': 'form-control', # boostraps
            'placeholder': 'Ingresar Usuario' # lo que aparece en el recuadro
            })
        )
    
    password = forms.CharField(
        label= 'Contraseña',
        widget= forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresar Contraseña'
            })
        )
    #relaciona el formulario con mi molode usuario y usa los campos internos 
    class Meta:
        model = Usuario
        fields = ['username', 'password']
    