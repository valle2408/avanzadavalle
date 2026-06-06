from django.urls import path # importamos las redirecciones
from . import views # importamos viwes de la carpeta principal
urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard')
]