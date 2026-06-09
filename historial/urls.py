from django.urls import path
from . import views

app_name = 'historial'

urlpatterns = [
    path('', views.lista_historial_compras, name='lista_historial_compras'),
]