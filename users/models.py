import random
from django.db import models
from django.core.validators import RegexValidator

def gerar_numero_conta():
    from .models import User
    while True:
        numero = str(random.randint(10000000, 99999999))  # 8 dígitos
        if not User.objects.filter(numero_da_conta=numero).exists():
            return numero
        
cpf_validator = RegexValidator(
    regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    message="CPF deve estar no formato XXX.XXX.XXX-XX"
)

telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\)\d{4,5}-\d{4}$',
    message="Telefone deve estar no formato (XX)XXXXX-XXXX"
)

class User(models.Model):
    numero_da_conta = models.CharField(max_length=20, unique=True, default=gerar_numero_conta)
    cpf = models.CharField(max_length=14, unique=True, validators=[cpf_validator])
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    data_de_nascimento = models.DateField()
    telefone = models.CharField(max_length=14, validators=[telefone_validator])
    # if(cliente estiver fazendo o cadastro por conta própria){
    #   Não tem opção de escolher o tipo de usuário (admUser = false)
    # } else {
    #   Se for o gerente cadastrando o cliente, ele pode escolher o tipo de usuário
    # }
    admUser = models.BooleanField(default=False)
    data_de_cadastro = models.DateTimeField(auto_now_add=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tipo_de_conta = models.CharField(max_length=20)
    status_conta = models.CharField(max_length=20, default='ativa')
