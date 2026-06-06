from django import forms
from.models import Comunidad # llamamos del modelo que hemos creado

#formulario de la comunudad
class FormularioComunidad(forms.ModelForm):

    class Meta:
        #trabajamos con comundiad
        model = Comunidad
        fields = ['nombre_comunidad', 'estado'] # son atributosque si podran llenar el usuario
        # los demas atributos los jalamos desd el sistema o lo ara el sistema como usuarios quien los creo y las fechas edicion etc
