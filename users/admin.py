from django.contrib import admin
from .models import Cliente, Gerente, SolicitacaoCredito

# Register your models here.
admin.site.register(Cliente)
admin.site.register(Gerente)
admin.site.register(SolicitacaoCredito)