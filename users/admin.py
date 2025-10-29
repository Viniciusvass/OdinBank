from django.contrib import admin
from .models import Cliente, Gerente, SolicitacaoCredito, Transferencia, Cartao, CartaoCliente

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Gerente)
admin.site.register(SolicitacaoCredito)
admin.site.register(Transferencia)
admin.site.register(Cartao)
admin.site.register(CartaoCliente)