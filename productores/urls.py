from django.urls import path
from . import views
#nombre de la app y vamos a utilizarla para lo general y las rutas
app_name = 'productores'
#rutas
urlpatterns = [
    # ruta primera osea principal despues del dashboard al modulo productres
    path('', views.lista_productores, name='lista_productores'),
    # cuando tocamos la accion ver detalles o solo ver
    path('<int:pk>/detalle/', views.detalle_productor, name='detalle_productor'),
    # la funcion de editar
    path('<int:pk>/editar/', views.editar_productor, name='editar_productor'),
]