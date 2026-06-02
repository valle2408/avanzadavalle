from django.urls import path # ayuda con las rutas, crea en realidad
from . import views # importamos views de usuarios
# creamos las urls 
urlpatterns = [
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
]