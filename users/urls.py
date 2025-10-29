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
    path('transferencia/', views.transferencia, name="transferencia"),
    path('extrato/', views.extrato, name='extrato'),
    path('cartoes/', views.listar_cartoes, name='listar_cartoes'),
    path('cartoes/solicitar/<int:cartao_id>/', views.solicitar_cartao, name='solicitar_cartao'),
    path('cartoes/solicitacoes/', views.solicitar_cartao, name='solicitacoes_cartao'),
    path('cartoes/aprovar/<int:solicitacao_id>/', views.aprovar_cartao, name='aprovar_cartao'),
    path('solicitacoes/cartoes/', views.lista_solicitacoes_cartao, name='lista_solicitacoes_cartao'),
    path('solicitacoes/cartoes/<int:solicitacao_id>/', views.responder_solicitacao_cartao, name='responder_solicitacao_cartao'),

]
