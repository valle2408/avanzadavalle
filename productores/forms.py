from django import forms
from .models import Productor


# formularioproductor  este formulario se usará para editar datos basicos del productor

class FormularioProductor(forms.ModelForm):

    class Meta:
    #indicamos que trabajara con la tabla productor
        model = Productor

        # atributos que podriamos editar los demas no por quesalen de comunidad y en el futuro de compras
        fields = [
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'comunidad',
            'estado',
        ]