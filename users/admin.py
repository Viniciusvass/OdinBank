from django.contrib import admin
from .models import Cliente, Gerente, SolicitacaoCredito, Transferencia

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Gerente)
admin.site.register(SolicitacaoCredito)
admin.site.register(Transferencia)