from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.lista_ventas, name='lista_ventas'),
    path('nueva/', views.nueva_venta, name='nueva_venta'),
    path('<int:pk>/editar/', views.editar_venta, name='editar_venta'),
    path('<int:pk>/comprobante/', views.comprobante_venta_pdf, name='comprobante_venta_pdf'),
]