import random
from django.db import models
from django.core.validators import RegexValidator
from django.apps import apps
from django.utils import timezone
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

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

def gerar_numero_cartao_unico():
    """Gera um número de cartão único com 16 dígitos."""
    while True:
        numero = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        if not CartaoCliente.objects.filter(numero_cartao=numero).exists():
            return numero

def gerar_senha_cartao():
    """Gera uma senha de 4 dígitos."""
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

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
            cliente.creditos = Decimal(str(cliente.creditos)) + Decimal(str(self.valor))
            cliente.save()

    def __str__(self):
        return f"Solicitação de {self.cliente.username} - R$ {self.valor} ({self.status})"

class Transferencia(models.Model):
    STATUS_CHOICES = [
        ('concluida', 'Concluída'),
        ('falhou', 'Falhou'),
    ]

    remetente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        related_name='transferencias_enviadas'
    )
    destinatario = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        related_name='transferencias_recebidas'
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data_transferencia = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='concluida')

    def clean(self):
        # Impedir transferência para si mesmo
        if self.remetente == self.destinatario:
            raise ValidationError("Você não pode transferir para si mesmo.")
        # Valor mínimo
        if self.valor <= 0:
            raise ValidationError("O valor da transferência deve ser maior que zero.")
        # Saldo suficiente
        if self.remetente.saldo < self.valor:
            raise ValidationError("Saldo insuficiente para realizar a transferência.")

    def save(self, *args, **kwargs):
        # Validação manual antes de salvar
        self.full_clean()

        # Atualiza saldos apenas se for uma nova transferência
        if not self.pk:
            self.remetente.saldo -= Decimal(self.valor)
            self.remetente.save()
            self.destinatario.saldo += Decimal(self.valor)
            self.destinatario.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transferência de {self.remetente.username} para {self.destinatario.username} - R$ {self.valor}"

class Cartao(models.Model):
    TIPO_CHOICES = [
        ('debito', 'Cartão de Débito'),
        ('credito', 'Cartão de Crédito'),
    ]

    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    limite_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    limite_maximo = models.DecimalField(max_digits=10, decimal_places=2)
    cor_hex = models.CharField(max_length=7, default="#FFFFFF")  # cor do cartão

    def __str__(self):
        return f"{self.nome} ({self.tipo})"

class CartaoCliente(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('negado', 'Negado'),
    ]

    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.CASCADE,
        related_name='cartoes_solicitados'
    )
    gerente = models.ForeignKey(
        'Gerente',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cartoes_gerenciados'
    )
    cartao = models.ForeignKey(
        'Cartao',
        on_delete=models.CASCADE,
        related_name='solicitacoes'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pendente'
    )
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    resposta_gerente = models.TextField(blank=True, null=True)

    numero_cartao = models.CharField(max_length=16, unique=True, blank=True, null=True)
    validade = models.DateField(blank=True, null=True)
    cvv = models.CharField(max_length=3, blank=True, null=True)
    senha = models.CharField(max_length=6, blank=True, null=True)  # agora em texto simples

    def clean(self):
        """Validações antes de salvar."""

        # Impede solicitar o mesmo cartão se já houver um aprovado
        if CartaoCliente.objects.filter(
            cliente=self.cliente,
            cartao=self.cartao,
            status='aprovado'
        ).exists():
            raise ValidationError("Você já possui este cartão aprovado.")

        # Impede solicitar cartão acima do limite disponível
        if self.cartao.limite_minimo > self.cliente.creditos:
            raise ValidationError("Seu limite atual não permite solicitar este cartão.")

    def save(self, *args, **kwargs):
        if self.pk:
            solicitacao_antiga = CartaoCliente.objects.get(pk=self.pk)
            status_antigo = solicitacao_antiga.status
        else:
            status_antigo = None

        self.full_clean()
        super().save(*args, **kwargs)

        # Quando o cartão é aprovado e ainda não possui número
        if self.status == 'aprovado' and status_antigo != 'aprovado':
            if not self.numero_cartao:
                self.numero_cartao = gerar_numero_cartao_unico()
                self.validade = timezone.now().date().replace(
                    year=timezone.now().year + 5
                )
                self.cvv = f"{random.randint(100, 999)}"
                self.senha = gerar_senha_cartao()  # agora texto simples
                super().save(update_fields=['numero_cartao', 'validade', 'cvv', 'senha'])

            print(f"Cartão {self.cartao.nome} aprovado para {self.cliente.username}")

    def __str__(self):
        return f"{self.cliente.username} - {self.cartao.nome} ({self.status})"
