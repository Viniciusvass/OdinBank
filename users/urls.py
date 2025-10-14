from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.view_login, name='login'),
    path('cadastro/', views.view_cadastro, name='cadastro'),
    path('perfil/', views.view_perfil, name='perfil'),
    path('cliente/<int:cliente_id>/', views.view_cliente_detalhes, name='cliente_detalhes'),
]
