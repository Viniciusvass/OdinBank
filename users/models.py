import random
from django.db import models
from django.core.validators import RegexValidator
from django.apps import apps

        
def gerar_numero_conta():
    Cliente = apps.get_model('users', 'Cliente')
    while True:
        numero = str(random.randint(10000000, 99999999))
        if not Cliente.objects.filter(numero_da_conta=numero).exists():
            return numero
        
cpf_validator = RegexValidator(
    regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    message="CPF deve estar no formato XXX.XXX.XXX-XX"
)

telefone_validator = RegexValidator(
    regex=r'^\(\d{2}\)\d{4,5}-\d{4}$',
    message="Telefone deve estar no formato (XX)XXXXX-XXXX"
)

class Gerente(models.Model):
    nome = models.CharField(max_length=150)
    cpf = models.CharField(max_length=14, unique=True, validators=[cpf_validator])
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=15, validators=[telefone_validator])
    matricula = models.CharField(max_length=20, unique=True)
    data_admissao = models.DateField()
    data_de_nascimento = models.DateField()
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    password = models.CharField(max_length=128)
    admUser = models.BooleanField(default=True)    

    def __str__(self):
        return f"{self.nome}"

class Cliente(models.Model):
    gerente_responsavel = models.ForeignKey(
        Gerente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clientes"
    )

    numero_da_conta = models.CharField(
        max_length=20,
        unique=True,
        default=gerar_numero_conta
    )
    cpf = models.CharField(max_length=14, unique=True, validators=[cpf_validator])
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    data_de_nascimento = models.DateField()
    telefone = models.CharField(max_length=14, validators=[telefone_validator])
    data_de_cadastro = models.DateTimeField(auto_now_add=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tipo_de_conta = models.CharField(
        max_length=20,
        choices=[
            ('corrente', 'Conta Corrente'),
            ('poupanca', 'Conta Poupança'),
            ('salario', 'Conta Salário'),
        ]
    )
    status_conta = models.CharField(max_length=20, default='ativa')
    admUser = models.BooleanField(default=False)
    creditos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.username}"
    
class SolicitacaoCredito(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('negado', 'Negado'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='solicitacoes'
    )
    gerente = models.ForeignKey(
        Gerente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitacoes_recebidas'
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.TextField()
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    resposta_gerente = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.pk:
            solicitacao_antiga = SolicitacaoCredito.objects.get(pk=self.pk)
            status_antigo = solicitacao_antiga.status
        else:
            status_antigo = None

        super().save(*args, **kwargs)

        if self.status == 'aprovado' and status_antigo != 'aprovado':
            cliente = self.cliente
            cliente.creditos += self.valor  # 👈 soma nos créditos
            cliente.save()

    def __str__(self):
        return f"Solicitação de {self.cliente.username} - R$ {self.valor} ({self.status})"
