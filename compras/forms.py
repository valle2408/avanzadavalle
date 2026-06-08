from django import forms
from django.utils import timezone

from comunidades.models import Comunidad


# FormularioCompraCafe:
# Este formulario recibe los datos principales de una nueva compra.
# Los pesajes se manejarán en el template con campos dinámicos,
# porque puede existir más de un pesaje por compra.
class FormularioCompraCafe(forms.Form):

    # Comunidad seleccionada desde la tabla Comunidades.
    # Mostraremos solo comunidades activas.
    comunidad = forms.ModelChoiceField(
        queryset=Comunidad.objects.filter(estado='Activo').order_by('nombre_comunidad'),
        label='Comunidad',
        empty_label='Seleccione una comunidad'
    )

    # Datos del productor.
    # Estos datos se usarán para buscar si ya existe el productor.
    # Si no existe, se creará automáticamente.
    nombre = forms.CharField(
        max_length=100,
        label='Nombre del productor'
    )

    apellido_paterno = forms.CharField(
        max_length=100,
        label='Apellido paterno'
    )

    apellido_materno = forms.CharField(
        max_length=100,
        label='Apellido materno',
        required=False
    )

    # Fecha de compra.
    # Se autocompleta con la fecha actual.
    fecha_compra = forms.DateField(
        label='Fecha de compra',
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    # Precio de compra por libra.
    # Se usa DecimalField para manejar dinero correctamente.
    precio_compra = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label='Precio de compra'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplicamos estilos parecidos a Comunidades y Productores.
        self.fields['comunidad'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
        })

        self.fields['nombre'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'autocomplete': 'off',
            'placeholder': 'Ejemplo: Juan',
        })

        self.fields['apellido_paterno'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'autocomplete': 'off',
            'placeholder': 'Ejemplo: Quispe',
        })

        self.fields['apellido_materno'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'autocomplete': 'off',
            'placeholder': 'Ejemplo: Mamani',
        })

        self.fields['fecha_compra'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
        })

        self.fields['precio_compra'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 pr-12 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'autocomplete': 'off',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0',
        })

    # Normaliza nombres y apellidos.
    # Ejemplo: "  juan  " -> "Juan"
    def limpiar_texto_nombre(self, texto):
        texto = texto.strip()
        texto = " ".join(texto.split())
        return texto.title()

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        return self.limpiar_texto_nombre(nombre)

    def clean_apellido_paterno(self):
        apellido_paterno = self.cleaned_data['apellido_paterno']
        return self.limpiar_texto_nombre(apellido_paterno)

    def clean_apellido_materno(self):
        apellido_materno = self.cleaned_data.get('apellido_materno', '')

        if apellido_materno:
            return self.limpiar_texto_nombre(apellido_materno)

        return ''

    def clean_precio_compra(self):
        precio = self.cleaned_data['precio_compra']

        if precio <= 0:
            raise forms.ValidationError('El precio de compra debe ser mayor a 0.')

        return precio