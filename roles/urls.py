from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('<int:pk>/cambiar-rol/', views.cambiar_rol_usuario, name='cambiar_rol_usuario'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('<int:pk>/resetear-password/', views.resetear_password_usuario, name='resetear_password_usuario'),
]
