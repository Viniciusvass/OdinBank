from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.view_login, name='login'),
    path('cadastro/', views.view_cadastro, name='cadastro'),
    path('perfil/', views.view_perfil, name='perfil'),
    path('cliente/<int:cliente_id>/', views.view_cliente_detalhes, name='cliente_detalhes'),
    path('solicitar-credito/', views.solicitar_credito, name='solicitar_credito'),
    path('solicitacoes/', views.lista_solicitacoes_gerente, name='lista_solicitacoes_gerente'),
    path('solicitacoes/<int:solicitacao_id>/', views.responder_solicitacao, name='responder_solicitacao'),
    path("transferencia/", views.transferencia, name="transferencia"),
    path('extrato/', views.extrato, name='extrato'),

]
