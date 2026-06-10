from django import forms
from django.utils import timezone

from .models import VentaCafe


class FormularioVentaCafe(forms.ModelForm):

    class Meta:
        model = VentaCafe
        fields = [
            'numero_ingreso',
            'fecha_venta',
            'empresa_compradora',
            'tipo_cafe',
            'cantidad_sacos',
            'peso_total_kg',
        ]

        widgets = {
            'fecha_venta': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.is_bound and not self.instance.pk:
            self.fields['fecha_venta'].initial = timezone.localdate()

        self.fields['numero_ingreso'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'autocomplete': 'off',
            'placeholder': 'Ejemplo: 000123',
        })

        self.fields['fecha_venta'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
        })

        self.fields['empresa_compradora'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'autocomplete': 'off',
            'placeholder': 'Ejemplo: Empresa compradora',
        })

        self.fields['tipo_cafe'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
        })

        self.fields['cantidad_sacos'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'min': '1',
            'placeholder': 'Ejemplo: 5',
        })

        self.fields['peso_total_kg'].widget.attrs.update({
            'class': 'w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#233b6e]',
            'min': '0.01',
            'step': '0.01',
            'placeholder': 'Ejemplo: 272.60',
        })

    def clean_numero_ingreso(self):
        numero_ingreso = self.cleaned_data['numero_ingreso'].strip()
        return numero_ingreso

    def clean_empresa_compradora(self):
        empresa = self.cleaned_data['empresa_compradora'].strip()
        empresa = " ".join(empresa.split())
        return empresa.title()