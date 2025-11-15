from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date
from decimal import Decimal
from .models import Gerente, Cliente, SolicitacaoCredito, Transferencia, Cartao, CartaoCliente
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from users.models import (
    Cliente, Gerente, Transferencia,
    Cartao, CartaoCliente
)
from django.contrib.auth.hashers import make_password

# Create your tests here.
"""Model - Gerente"""
class GerenteModelTest(TestCase):
    def setUp(self):
        self.gerente = Gerente.objects.create(
            nome="João Silva",
            cpf="123.456.789-00",
            email="joao@example.com",
            telefone="(11) 99999-9999",
            matricula="G001",
            data_admissao=date(2023, 5, 1),
            data_de_nascimento=date(1990, 7, 20),
            salario=8500.00,
            password="senhaSegura123",
            admUser=True
        )

    def test_gerente_criado_com_sucesso(self):
        """Verifica se o gerente foi criado corretamente"""
        self.assertEqual(self.gerente.nome, "João Silva")
        self.assertEqual(self.gerente.cpf, "123.456.789-00")
        self.assertEqual(self.gerente.email, "joao@example.com")
        self.assertTrue(self.gerente.admUser)

    def test_str_retorna_nome(self):
        """Verifica se o método __str__ retorna o nome"""
        self.assertEqual(str(self.gerente), "João Silva")

    def test_campos_unicos(self):
        """Verifica se cpf, email e matrícula são únicos"""
        with self.assertRaises(IntegrityError):
            Gerente.objects.create(
                nome="Maria Oliveira",
                cpf="123.456.789-00",  # mesmo CPF
                email="maria@example.com",
                telefone="(11) 98888-8888",
                matricula="G002",
                data_admissao=date(2023, 6, 1),
                data_de_nascimento=date(1992, 8, 15),
                salario=9000.00,
                password="outraSenha123",
                admUser=False
            )

    def test_validacao_campos_obrigatorios(self):
        """Verifica se o modelo exige campos obrigatórios"""
        gerente_invalido = Gerente(
            nome="",
            cpf="",
            email="",
            telefone="",
            matricula="",
            data_admissao=None,
            data_de_nascimento=None,
            salario=None,
            password=""
        )
        with self.assertRaises(ValidationError):
            gerente_invalido.full_clean()  # chama as validações de campo

"""Model - Cliente"""
class ClienteModelTest(TestCase):
    def setUp(self):
        # Cria um gerente para associar ao cliente
        self.gerente = Gerente.objects.create(
            nome="João Gerente",
            cpf="123.456.789-00",
            email="gerente@example.com",
            telefone="(11) 99999-9999",
            matricula="G001",
            data_admissao=date(2023, 1, 1),
            data_de_nascimento=date(1985, 5, 10),
            salario=9500.00,
            password="senha123",
            admUser=True
        )

        # Cria um cliente
        self.cliente = Cliente.objects.create(
            gerente_responsavel=self.gerente,
            cpf="987.654.321-00",
            username="maria_cliente",
            email="maria@example.com",
            password="senhaSegura123",
            data_de_nascimento=date(1995, 3, 15),
            telefone="(11) 98888-8888",
            saldo=1000.00,
            tipo_de_conta="corrente",
            status_conta="ativa",
            creditos=500.00
        )

    def test_cliente_criado_com_sucesso(self):
        """Verifica se o cliente foi criado corretamente"""
        self.assertEqual(self.cliente.username, "maria_cliente")
        self.assertEqual(self.cliente.gerente_responsavel, self.gerente)
        self.assertEqual(self.cliente.tipo_de_conta, "corrente")
        self.assertEqual(self.cliente.status_conta, "ativa")
        self.assertAlmostEqual(self.cliente.saldo, 1000.00)
        self.assertAlmostEqual(self.cliente.creditos, 500.00)

    def test_str_retorna_username(self):
        """Verifica se o método __str__ retorna o username"""
        self.assertEqual(str(self.cliente), "maria_cliente")

    def test_campos_unicos(self):
        """Verifica se cpf, email e número da conta são únicos"""
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(
                gerente_responsavel=self.gerente,
                cpf="987.654.321-00",  # mesmo CPF
                username="outro_cliente",
                email="outro@example.com",
                password="senhaOutra123",
                data_de_nascimento=date(1990, 6, 20),
                telefone="(11) 97777-7777",
                tipo_de_conta="poupanca",
                status_conta="ativa"
            )

    def test_validacao_campos_obrigatorios(self):
        """Verifica se os campos obrigatórios são realmente exigidos"""
        cliente_invalido = Cliente(
            cpf="",
            username="",
            email="",
            password="",
            data_de_nascimento=None,
            telefone="",
            tipo_de_conta=""
        )
        with self.assertRaises(ValidationError):
            cliente_invalido.full_clean()

'''Model - SolicitaçaoCredito'''
class SolicitacaoCreditoModelTest(TestCase):
    def setUp(self):
        # Cria um gerente
        self.gerente = Gerente.objects.create(
            nome="Carlos Gerente",
            cpf="111.222.333-44",
            email="carlos@example.com",
            telefone="(11) 90000-0000",
            matricula="G002",
            data_admissao=date(2022, 5, 10),
            data_de_nascimento=date(1980, 2, 15),
            salario=10000.00,
            password="senhaForte123",
            admUser=True
        )

        # Cria um cliente
        self.cliente = Cliente.objects.create(
            gerente_responsavel=self.gerente,
            cpf="999.888.777-66",
            username="joana_cliente",
            email="joana@example.com",
            password="senhaSegura123",
            data_de_nascimento=date(1993, 4, 10),
            telefone="(11) 95555-5555",
            saldo=2000.00,
            tipo_de_conta="corrente",
            status_conta="ativa",
            creditos=0.00
        )

        # Cria uma solicitação inicial
        self.solicitacao = SolicitacaoCredito.objects.create(
            cliente=self.cliente,
            gerente=self.gerente,
            valor=Decimal('500.00'),
            motivo="Compra de equipamento de trabalho"
        )

    def test_solicitacao_criada_com_sucesso(self):
        """Verifica se a solicitação foi criada com status pendente"""
        self.assertEqual(self.solicitacao.status, "pendente")
        self.assertEqual(self.solicitacao.cliente, self.cliente)
        self.assertEqual(self.solicitacao.valor, Decimal('500.00'))
        self.assertEqual(str(self.solicitacao), "Solicitação de joana_cliente - R$ 500.00 (pendente)")

    def test_aprovacao_credito_aumenta_creditos_cliente(self):
        """Verifica se aprovar uma solicitação soma o valor nos créditos do cliente"""
        creditos_iniciais = Decimal(str(self.cliente.creditos))  # 👈 conversão segura
        self.solicitacao.status = "aprovado"
        self.solicitacao.save()

        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.creditos, creditos_iniciais + Decimal('500.00'))
        
    def test_negacao_credito_nao_altera_creditos(self):
        """Verifica se negar uma solicitação não altera os créditos"""
        creditos_iniciais = self.cliente.creditos
        self.solicitacao.status = "negado"
        self.solicitacao.save()

        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.creditos, creditos_iniciais)

    def test_aprovar_duas_vezes_nao_soma_credito_duplicado(self):
        """Verifica se aprovar uma solicitação já aprovada não duplica o valor nos créditos"""
        self.solicitacao.status = "aprovado"
        self.solicitacao.save()

        # Tenta salvar novamente com o mesmo status "aprovado"
        self.solicitacao.save()
        self.cliente.refresh_from_db()

        # Deve ter somado apenas uma vez
        self.assertEqual(self.cliente.creditos, Decimal('500.00'))

"""Model - Transferencia"""
class TransferenciaModelTest(TestCase):
    def setUp(self):
        # Cria um gerente
        self.gerente = Gerente.objects.create(
            nome="Carlos Gerente",
            cpf="111.222.333-44",
            email="carlos@example.com",
            telefone="(11) 90000-0000",
            matricula="G001",
            data_admissao=date(2020, 5, 10),
            data_de_nascimento=date(1980, 2, 15),
            salario=Decimal("10000.00"),
            password="senha123",
            admUser=True
        )

        # Cria dois clientes
        self.cliente1 = Cliente.objects.create(
            gerente_responsavel=self.gerente,
            cpf="999.888.777-66",
            username="joao",
            email="joao@example.com",
            password="senha123",
            data_de_nascimento=date(1990, 1, 1),
            telefone="(11) 99999-9999",
            saldo=Decimal("1000.00"),
            tipo_de_conta="corrente",
            status_conta="ativa",
        )

        self.cliente2 = Cliente.objects.create(
            gerente_responsavel=self.gerente,
            cpf="555.444.333-22",
            username="maria",
            email="maria@example.com",
            password="senha456",
            data_de_nascimento=date(1995, 5, 5),
            telefone="(11) 98888-8888",
            saldo=Decimal("500.00"),
            tipo_de_conta="corrente",
            status_conta="ativa",
        )

    def test_transferencia_concluida_com_sucesso(self):
        """Verifica se a transferência entre clientes é concluída corretamente"""
        transferencia = Transferencia.objects.create(
            remetente=self.cliente1,
            destinatario=self.cliente2,
            valor=Decimal("200.00"),
        )

        self.cliente1.refresh_from_db()
        self.cliente2.refresh_from_db()

        self.assertEqual(transferencia.status, "concluida")
        self.assertEqual(self.cliente1.saldo, Decimal("800.00"))
        self.assertEqual(self.cliente2.saldo, Decimal("700.00"))

    def test_transferencia_para_si_mesmo_lanca_erro(self):
        """Impede que o cliente envie transferência para si mesmo"""
        transferencia = Transferencia(
            remetente=self.cliente1,
            destinatario=self.cliente1,
            valor=Decimal("100.00"),
        )
        with self.assertRaises(ValidationError):
            transferencia.full_clean()

    def test_transferencia_com_valor_negativo_lanca_erro(self):
        """Impede transferências com valor menor ou igual a zero"""
        transferencia = Transferencia(
            remetente=self.cliente1,
            destinatario=self.cliente2,
            valor=Decimal("-10.00"),
        )
        with self.assertRaises(ValidationError):
            transferencia.full_clean()

    def test_transferencia_com_saldo_insuficiente(self):
        """Impede transferência se o saldo do remetente for insuficiente"""
        transferencia = Transferencia(
            remetente=self.cliente1,
            destinatario=self.cliente2,
            valor=Decimal("2000.00"),  # maior que o saldo
        )
        with self.assertRaises(ValidationError):
            transferencia.full_clean()

    def test_repr_transferencia(self):
        """Verifica o método __str__ da transferência"""
        transferencia = Transferencia.objects.create(
            remetente=self.cliente1,
            destinatario=self.cliente2,
            valor=Decimal("100.00"),
        )
        self.assertEqual(
            str(transferencia),
            "Transferência de joao para maria - R$ 100.00"
        )

"""Model - Cartao"""
class CartaoModelTest(TestCase):
    def setUp(self):
        self.cartao = Cartao.objects.create(
            nome="Odin Black",
            descricao="Cartão de crédito premium com benefícios exclusivos.",
            tipo="credito",
            limite_minimo=Decimal("1000.00"),
            limite_maximo=Decimal("10000.00"),
            cor_hex="#000000"
        )

    def test_cartao_criado_com_sucesso(self):
        """Verifica se o cartão foi criado corretamente"""
        self.assertEqual(self.cartao.nome, "Odin Black")
        self.assertEqual(self.cartao.tipo, "credito")
        self.assertEqual(self.cartao.limite_minimo, Decimal("1000.00"))
        self.assertEqual(self.cartao.limite_maximo, Decimal("10000.00"))
        self.assertEqual(self.cartao.cor_hex, "#000000")

    def test_str_retorna_nome_e_tipo(self):
        """Verifica o método __str__ do modelo Cartao"""
        self.assertEqual(str(self.cartao), "Odin Black (credito)")

    def test_nome_unico(self):
        """Verifica se o campo nome é realmente único"""
        with self.assertRaises(Exception):  # IntegrityError ou ValidationError
            Cartao.objects.create(
                nome="Odin Black",  # mesmo nome
                descricao="Outro cartão",
                tipo="debito",
                limite_minimo=Decimal("100.00"),
                limite_maximo=Decimal("500.00"),
                cor_hex="#FFFFFF"
            )

    def test_limites_sao_decimais(self):
        """Garante que os limites sejam armazenados como Decimal"""
        self.assertIsInstance(self.cartao.limite_minimo, Decimal)
        self.assertIsInstance(self.cartao.limite_maximo, Decimal)

"""Model - CartaoCliente"""
class CartaoClienteModelTest(TestCase):
    def setUp(self):
        self.gerente = Gerente.objects.create(
        nome="Carlos Gerente",
        cpf="111.222.333-44",
        email="carlos@example.com",
        telefone="(11) 90000-0000",
        matricula="G002",
        data_admissao=date(2022, 5, 10),
        data_de_nascimento=date(1980, 2, 15),
        salario=Decimal('10000.00'),
        password=make_password("senhaForte123"),
        admUser=True
    )

        self.cliente = Cliente.objects.create(
            gerente_responsavel=self.gerente,
            cpf="999.888.777-66",
            username="joana_cliente",
            email="joana@example.com",
            password=make_password("senhaSegura123"),
            data_de_nascimento=date(1993, 4, 10),
            telefone="(11) 95555-5555",
            saldo=Decimal('2000.00'),
            tipo_de_conta="corrente",
            status_conta="ativa",
            creditos=Decimal('2000.00')
        )

        self.cartao = Cartao.objects.create(
            nome="Cartão Ouro",
            descricao="Cartão de crédito premium",
            tipo="credito",
            limite_minimo=Decimal('1000.00'),
            limite_maximo=Decimal('5000.00'),
            cor_hex="#FFD700"
        )

    def test_criar_solicitacao_pendente(self):
        """Cria solicitação pendente com sucesso."""
        solicitacao = CartaoCliente.objects.create(
            cliente=self.cliente,
            gerente=self.gerente,
            cartao=self.cartao
        )
        self.assertEqual(solicitacao.status, "pendente")
        self.assertIsNone(solicitacao.numero_cartao)

    def test_impedir_cartao_acima_limite(self):
        """Cliente com crédito insuficiente não pode solicitar o cartão."""
        self.cliente.creditos = Decimal('500.00')
        self.cliente.save()

        solicitacao = CartaoCliente(
            cliente=self.cliente,
            gerente=self.gerente,
            cartao=self.cartao
        )
        with self.assertRaises(ValidationError):
            solicitacao.full_clean()

    def test_impedir_cartao_repetido_aprovado(self):
        """Não deve permitir solicitar o mesmo cartão já aprovado."""
        CartaoCliente.objects.create(
            cliente=self.cliente,
            gerente=self.gerente,
            cartao=self.cartao,
            status='aprovado'
        )

        nova = CartaoCliente(
            cliente=self.cliente,
            gerente=self.gerente,
            cartao=self.cartao
        )
        with self.assertRaises(ValidationError):
            nova.full_clean()

    def test_gerar_dados_cartao_quando_aprovado(self):
        """Quando aprovado, o cartão deve gerar número, validade, cvv e senha."""
        solicitacao = CartaoCliente.objects.create(
            cliente=self.cliente,
            gerente=self.gerente,
            cartao=self.cartao,
            status='pendente'
        )

        solicitacao.status = 'aprovado'
        solicitacao.save()

        solicitacao.refresh_from_db()
        self.assertIsNotNone(solicitacao.numero_cartao)
        self.assertIsNotNone(solicitacao.validade)
        self.assertIsNotNone(solicitacao.cvv)
        self.assertIsNotNone(solicitacao.senha)

    def test_str_retorna_formatado(self):
        """Verifica o método __str__."""
        solicitacao = CartaoCliente.objects.create(
            cliente=self.cliente,
            gerente=self.gerente,
            cartao=self.cartao
        )
        self.assertEqual(str(solicitacao), f"{self.cliente.username} - {self.cartao.nome} (pendente)")

"""Views"""
class UsersViewsTests(TestCase):
    def setUp(self):
        """Cria usuários, cartões e cliente de teste."""
        self.client = Client()

        # Gerente
        self.gerente = Gerente.objects.create(
            nome="Gerente Teste",
            cpf="111.111.111-11",
            email="gerente@teste.com",
            telefone="(11)99999-9999",
            matricula="G001",
            data_admissao="2020-01-01",
            data_de_nascimento="1980-01-01",
            salario=10000,
            password=make_password("123"),
        )

        # Cliente
        self.cliente = Cliente.objects.create(
            cpf="222.222.222-22",
            username="cliente1",
            email="cliente@teste.com",
            telefone="(11)88888-8888",
            tipo_de_conta="corrente",
            saldo=Decimal("1000.00"),
            creditos=Decimal("1000.00"),  # ← garante que a validação do CartaoCliente passe
            password=make_password("123"),
            gerente_responsavel=self.gerente,
            data_de_nascimento="1990-01-01"  # ← adicione esta linha
        )

        self.cartao_credito = Cartao.objects.create(
            nome="Cartão Gold",
            descricao="Crédito ouro",
            tipo="credito",
            limite_minimo=500,
            limite_maximo=5000,
            cor_hex="#FFD700",
        )

        self.cartao_debito = Cartao.objects.create(
            nome="Cartão Débito",
            descricao="Cartão de débito",
            tipo="debito",
            limite_minimo=0,
            limite_maximo=0,
            cor_hex="#FFFFFF",
        )
        
    # -------------------
    # VIEW CADASTRO
    # -------------------
    def test_view_cadastro_get(self):
        resp = self.client.get(reverse("users:cadastro"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/cadastro/index.html")

    def test_view_cadastro_post_sucesso(self):
        data = {
            "cpf": "333.333.333-33",
            "username": "novo",
            "email": "novo@teste.com",
            "password": "123",
            "data_de_nascimento": "2000-01-01",
            "telefone": "(11)77777-7777",
            "tipo_de_conta": "corrente",
        }
        resp = self.client.post(reverse("users:cadastro"), data, follow=True)
        self.assertRedirects(resp, reverse("users:login"))
        self.assertTrue(Cliente.objects.filter(email="novo@teste.com").exists())
    
    # -------------------
    # VIEW LOGIN
    # -------------------
    def test_login_cliente_sucesso(self):
        data = {"email": "cliente@teste.com", "password": "123"}
        resp = self.client.post(reverse("users:login"), data, follow=True)
        self.assertRedirects(resp, reverse("users:perfil"))
        self.assertIn("user_id", self.client.session)

    def test_login_erro_usuario_invalido(self):
        data = {"email": "naoexiste@teste.com", "password": "123"}
        resp = self.client.post(reverse("users:login"), data)
        self.assertContains(resp, "Usuário ou senha inválidos")
        
    # -------------------
    # VIEW PERFIL
    # -------------------
    def test_perfil_cliente(self):
        session = self.client.session
        session["user_id"] = self.cliente.id
        session["admUser"] = False
        session.save()

        resp = self.client.get(reverse("users:perfil"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/perfil/cliente/index.html")

    def test_perfil_gerente(self):
        session = self.client.session
        session["user_id"] = self.gerente.id
        session["admUser"] = True
        session.save()

        resp = self.client.get(reverse("users:perfil"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/perfil/gerente/index.html")

    # -------------------
    # VIEW TRANSFERÊNCIA
    # -------------------
    def test_transferencia_sucesso(self):
        destinatario = Cliente.objects.create(
            cpf="999.999.999-99",
            username="cliente2",
            email="cliente2@teste.com",
            telefone="(11)66666-6666",
            tipo_de_conta="corrente",
            saldo=Decimal("500.00"),
            password=make_password("123"),
            data_de_nascimento="2000-01-01"  # ✅ Adicione esta linha
        )

        session = self.client.session
        session["user_id"] = self.cliente.id
        session["admUser"] = False
        session.save()

        data = {"cpf": destinatario.cpf, "valor": "100.00"}
        resp = self.client.post(reverse("users:transferencia"), data, follow=True)
        self.assertRedirects(resp, reverse("users:transferencia"))
        destinatario.refresh_from_db()
        self.assertEqual(destinatario.saldo, Decimal("600.00"))

    def test_transferencia_saldo_insuficiente(self):
        destinatario = Cliente.objects.create(
            cpf="888.888.888-88",
            username="cliente3",
            email="cliente3@teste.com",
            telefone="(11)55555-5555",
            tipo_de_conta="corrente",
            saldo=Decimal("0.00"),
            password=make_password("123"),
            data_de_nascimento="2000-01-01",  # 👈 adicione isso
        )

        session = self.client.session
        session["user_id"] = self.cliente.id
        session["admUser"] = False
        session.save()

        data = {"cpf": destinatario.cpf, "valor": "99999.00"}
        resp = self.client.post(reverse("users:transferencia"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Saldo insuficiente")

    # -------------------
    # VIEW EXTRATO
    # -------------------
    def test_extrato_cliente(self):
        session = self.client.session
        session["user_id"] = self.cliente.id
        session["admUser"] = False
        session.save()

        resp = self.client.get(reverse("users:extrato"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/perfil/cliente/extrato.html")

    # -------------------
    # VIEW LISTAR CARTÕES
    # -------------------
    def test_listar_cartoes(self):
        session = self.client.session
        session["user_id"] = self.cliente.id
        session.save()

        resp = self.client.get(reverse("users:listar_cartoes"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/perfil/cliente/listar_cartoes.html")
        
    # -------------------
    # VIEW SOLICITAR CARTÃO
    # -------------------
    def test_solicitar_cartao(self):
        session = self.client.session
        session["user_id"] = self.cliente.id
        session.save()

        data = {}
        resp = self.client.post(
            reverse("users:solicitar_cartao", args=[self.cartao_credito.id]),
            data,
            follow=True,
        )
        self.assertRedirects(resp, reverse("users:listar_cartoes"))
        self.assertTrue(
            CartaoCliente.objects.filter(cliente=self.cliente, cartao=self.cartao_credito).exists()
        )

    # -------------------
    # VIEW MEUS CARTÕES
    # -------------------
    def test_meus_cartoes(self):
        CartaoCliente.objects.create(cliente=self.cliente, cartao=self.cartao_credito, status="pendente")
        session = self.client.session
        session["user_id"] = self.cliente.id
        session["admUser"] = False
        session.save()

        resp = self.client.get(reverse("users:meus_cartoes"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/perfil/cliente/meus_cartoes.html")

    # -------------------
    # VIEW GERENTE: SOLICITAÇÕES DE CARTÕES
    # -------------------
    def test_visualizar_solicitacoes_cartoes(self):
        CartaoCliente.objects.create(cliente=self.cliente, cartao=self.cartao_credito, status="pendente")
        session = self.client.session
        session["user_id"] = self.gerente.id
        session["admUser"] = True
        session.save()

        resp = self.client.get(reverse("users:solicitacoes_cartoes"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "users/perfil/gerente/solicitacoes_cartoes.html")

    def test_aprovar_ou_negar_cartao(self):
        solicitacao = CartaoCliente.objects.create(
            cliente=self.cliente, cartao=self.cartao_credito, status="pendente"
        )

        session = self.client.session
        session["user_id"] = self.gerente.id
        session["admUser"] = True
        session.save()

        resp = self.client.get(
            reverse("users:aprovar_ou_negar_cartao", args=[solicitacao.id, "aprovar"]),
            follow=True,
        )
        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, "aprovado")

