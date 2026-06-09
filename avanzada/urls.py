"""
URL configuration for avanzada project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin # importa el panel de adminsitracion
from django.urls import path, include # para incluir rutas y otras rutas
from django.views.generic import RedirectView # con esto directo a login nos mandara

urlpatterns = [
    path('admin/', admin.site.urls), # ruta del admin
    path('',include('usuarios.urls')), # rutas de los uusuarios
    path('',include('principal.urls')), # rutas del dashboard o principal
    path('comunidades/', include('comunidades.urls')), # de la comunidad
    path('', RedirectView.as_view(pattern_name='login', permanent=False)), # para la redirecciona al login directamente
    path('productores/', include('productores.urls')), # agregamos las acciones de productres
    path('compras/', include('compras.urls')),# para las compras
    path('historial-compras/', include('historial.urls')), # para el historial
]
