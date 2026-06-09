from django.urls import path
from . import views


# Nombre de la app compras.
# Permitirá usar rutas como:
# {% url 'compras:nueva_compra' %}
app_name = 'compras'


urlpatterns = [
    # Formulario principal de Registrar compra de café / Nueva compra
    path('nueva/', views.nueva_compra, name='nueva_compra'),

    # Recibo PDF pequeño tipo ticket
    path('<int:pk>/recibo/', views.recibo_compra_pdf, name='recibo_compra_pdf'),
]