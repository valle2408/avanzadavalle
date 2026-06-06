# urls para la carga y direccionamiento de las funcionalidades y htmls que vamos a realizar 
from django.urls import path # el path para viajar
from . import views # expotamos las logicas del viwes que heoms hecho

app_name = 'comunidades' # nombre de la app para utilizar

#rutas
urlpatterns = [
    path('', views.lista_comunidades, name='lista_comunidades'), # para litar
    path('crear/', views.crear_comunidad, name='crear_comunidad'), # para crear
    path('<int:pk>/editar/', views.editar_comunidad, name='editar_comunidad'),# para editar
    path('<int:pk>/eliminar/', views.eliminar_comunidad, name='eliminar_comunidad'), # para eliminar pensarlo bien aun
    
]
