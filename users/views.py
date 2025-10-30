from django.shortcuts import redirect, render
from .models import Cliente, Gerente, Transferencia
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from .models import SolicitacaoCredito
from .forms import SolicitacaoCreditoForm
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Cartao, CartaoCliente

# Create your views here.
def view_cadastro(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        data_str = request.POST.get('data_de_nascimento')
        telefone = request.POST.get('telefone')
        tipo_de_conta = request.POST.get('tipo_de_conta')

        # Converte a data de nascimento para o tipo Date
        try:
            data_de_nascimento = datetime.strptime(data_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, 'Data de nascimento inválida!')
            return render(request, 'users/cadastro/index.html')

        # Verifica se já existe e-mail ou CPF cadastrados
        if Cliente.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado!')
            return render(request, 'users/cadastro/index.html')

        if Cliente.objects.filter(cpf=cpf).exists():
            messages.error(request, 'Este CPF já está cadastrado!')
            return render(request, 'users/cadastro/index.html')

        new_cliente = Cliente(
            cpf=cpf,
            username=username,
            email=email,
            password=password,
            data_de_nascimento=data_de_nascimento,
            telefone=telefone,
            tipo_de_conta=tipo_de_conta
        )
        new_cliente.save()
        messages.success(request, 'Cadastro realizado com sucesso!')
        return redirect('users:login')

    return render(request, 'users/cadastro/index.html')

def view_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = None

        # Primeiro tenta achar um gerente
        try:
            user = Gerente.objects.get(email=email)
        except Gerente.DoesNotExist:
            # Se não for gerente, tenta achar um cliente
            try:
                user = Cliente.objects.get(email=email)
            except Cliente.DoesNotExist:
                return render(
                    request,
                    "users/login/index.html",
                    {"error": "Usuário ou senha inválidos"}
                )

        # Verifica senha criptografada
        if check_password(password, user.password):
            request.session["user_id"] = user.id
            request.session["admUser"] = user.admUser
            return redirect("users:perfil")
        else:
            return render(
                request,
                "users/login/index.html",
                {"error": "Usuário ou senha inválidos"}
            )

    return render(request, "users/login/index.html")

def view_perfil(request):
    if "user_id" not in request.session:
        return redirect("users:login")

    user_id = request.session["user_id"]
    admUser = request.session.get("admUser", False)

    if admUser:
        user = Gerente.objects.get(id=user_id)
        clientes = user.clientes.all()
        
        # Separar clientes por status
        clientes_ativos = clientes.filter(status_conta='ativa')
        clientes_inativos = clientes.filter(status_conta='inativa')
        clientes_bloqueados = clientes.filter(status_conta='bloqueada')
        
        # Somatório de saldo apenas dos ativos
        saldo_total = clientes_ativos.aggregate(total=Sum('saldo'))['total'] or 0

        return render(
            request,
            "users/perfil/gerente/index.html",
            {
                "user": user,
                "clientes": clientes,
                "clientes_ativos": clientes_ativos,
                "clientes_inativos": clientes_inativos,
                "clientes_bloqueados": clientes_bloqueados,
                "saldo_total": saldo_total,
            }
        )

    # Se for cliente
    user = Cliente.objects.get(id=user_id)
    return render(request, "users/perfil/cliente/index.html", {"user": user})

def view_cliente_detalhes(request, cliente_id):
    if "user_id" not in request.session:
        return redirect("users:login")

    admUser = request.session.get("admUser", False)
    if not admUser:
        return redirect("users:perfil")

    cliente = Cliente.objects.get(id=cliente_id)

    # 🔹 Se o gerente enviou o formulário
    if request.method == "POST":
        cliente.username = request.POST.get("username")
        cliente.cpf = request.POST.get("cpf")
        cliente.email = request.POST.get("email")
        cliente.telefone = request.POST.get("telefone")
        cliente.tipo_de_conta = request.POST.get("tipo_de_conta")
        cliente.status_conta = request.POST.get("status_conta")
        cliente.saldo = request.POST.get("saldo")

        cliente.save()

        from django.contrib import messages
        messages.success(request, "Dados do cliente atualizados com sucesso!")
        return redirect("users:cliente_detalhes", cliente_id=cliente.id)

    return render(request, "users/perfil/gerente/cliente_detalhes.html", {"cliente": cliente})

def solicitar_credito(request):
    cliente_id = request.session.get("user_id")
    cliente = get_object_or_404(Cliente, id=cliente_id)

    if request.method == "POST":
        form = SolicitacaoCreditoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.cliente = cliente
            solicitacao.gerente = cliente.gerente_responsavel
            solicitacao.save()
            return redirect('users:perfil')  # ajuste para sua rota
    else:
        form = SolicitacaoCreditoForm()

    return render(request, 'users/perfil/cliente/solicitar_credito.html', {'form': form})

def lista_solicitacoes_gerente(request):
    gerente_id = request.session.get("user_id")
    gerente = get_object_or_404(Gerente, id=gerente_id)
    solicitacoes = SolicitacaoCredito.objects.filter(gerente=gerente).order_by('-data_solicitacao')

    return render(request, 'users/perfil/gerente/solicitacoes.html', {'gerente': gerente, 'solicitacoes': solicitacoes})


def responder_solicitacao(request, solicitacao_id):
    solicitacao = get_object_or_404(SolicitacaoCredito, id=solicitacao_id)

    if request.method == "POST":
        acao = request.POST.get("acao")
        resposta = request.POST.get("resposta")

        if acao == "aprovar":
            solicitacao.status = "aprovado"
        elif acao == "negar":
            solicitacao.status = "negado"

        solicitacao.resposta_gerente = resposta
        solicitacao.save()

        messages.success(request, f"Solicitação {solicitacao.id} atualizada com sucesso!")
        return redirect('users:lista_solicitacoes_gerente')

    return render(request, 'users/perfil/gerente/responder_solicitacao.html', {'solicitacao': solicitacao})

def transferencia(request):
    # Garante que o usuário está logado e é um cliente
    if "user_id" not in request.session:
        return redirect("users:login")

    admUser = request.session.get("admUser", False)
    if admUser:
        messages.error(request, "Apenas clientes podem realizar transferências.")
        return redirect("users:perfil")

    remetente = get_object_or_404(Cliente, id=request.session["user_id"])

    if request.method == "POST":
        cpf_destinatario = request.POST.get("cpf", "").strip()
        valor = request.POST.get("valor", "").strip()

        # Verifica campos obrigatórios
        if not cpf_destinatario or not valor:
            messages.error(request, "Preencha todos os campos.")
            return redirect("users:transferencia")

        # Valida o valor informado
        try:
            valor = Decimal(valor)
        except:
            messages.error(request, "Valor inválido.")
            return redirect("users:transferencia")

        # Busca o destinatário pelo CPF
        try:
            destinatario = Cliente.objects.get(cpf=cpf_destinatario)
        except Cliente.DoesNotExist:
            messages.error(request, "CPF do destinatário não encontrado.")
            return redirect("users:transferencia")

        # Cria a transferência
        transferencia = Transferencia(
            remetente=remetente,
            destinatario=destinatario,
            valor=valor
        )

        try:
            transferencia.save()
            messages.success(
                request,
                f"Transferência de R$ {valor:.2f} para {destinatario.username} realizada com sucesso!"
            )
            # Mantém o usuário na mesma página após a transferência
            return redirect("users:transferencia")

        except ValidationError as e:
            # Captura mensagens do modelo (ex: saldo insuficiente, transferência para si mesmo)
            for msg in e.messages:
                messages.error(request, msg)
        except Exception as e:
            messages.error(request, f"Erro ao processar transferência: {e}")

    # Renderiza a página (tanto GET quanto erros no POST)
    return render(request, "users/perfil/cliente/transferencia.html", {"user": remetente})

def extrato(request):
    # Garante que o usuário está logado e é um cliente
    if "user_id" not in request.session:
        return redirect("users:login")

    admUser = request.session.get("admUser", False)
    if admUser:
        messages.error(request, "Apenas clientes podem acessar o extrato.")
        return redirect("users:perfil")

    # Pega o cliente logado
    cliente = get_object_or_404(Cliente, id=request.session["user_id"])

    # Busca transferências enviadas e recebidas
    transferencias_enviadas = cliente.transferencias_enviadas.all()
    transferencias_recebidas = cliente.transferencias_recebidas.all()

    # Combina e ordena por data
    todas_transferencias = sorted(
        list(transferencias_enviadas) + list(transferencias_recebidas),
        key=lambda t: t.data_transferencia,
        reverse=True
    )

    context = {
        "user": cliente,
        "transferencias": todas_transferencias,
    }
    return render(request, 'users/perfil/cliente/extrato.html', context)

def listar_cartoes(request):
    if "user_id" not in request.session:
        return redirect("users:login")

    cliente = get_object_or_404(Cliente, id=request.session["user_id"])
    cartoes = Cartao.objects.all()

    # Separar cartões por tipo
    cartao_debito = next((c for c in cartoes if c.tipo == 'debito'), None)
    creditos = [c for c in cartoes if c.tipo == 'credito']

    context = {
        "user": cliente,
        "cartao_debito": cartao_debito,
        "cartao_credito1": creditos[0] if len(creditos) > 0 else None,
        "cartao_credito2": creditos[1] if len(creditos) > 1 else None,
        "cartao_credito3": creditos[2] if len(creditos) > 2 else None,
    }

    return render(request, "users/perfil/cliente/listar_cartoes.html", context)

def solicitar_cartao(request, cartao_id):
    if "user_id" not in request.session:
        return redirect("users:login")

    cliente = get_object_or_404(Cliente, id=request.session["user_id"])
    cartao = get_object_or_404(Cartao, id=cartao_id)

    # 🔒 Impede solicitações duplicadas
    solicitacao_existente = CartaoCliente.objects.filter(cliente=cliente, cartao=cartao).exclude(status="negado").exists()
    if solicitacao_existente:
        messages.warning(request, f"Você já possui uma solicitação ou um cartão {cartao.nome}.")
        return redirect("users:listar_cartoes")

    if request.method == "POST":
        try:
            CartaoCliente.objects.create(
                cliente=cliente,
                cartao=cartao,
                status="pendente"
            )
            messages.success(request, f"Sua solicitação do cartão {cartao.nome} foi enviada com sucesso!")
            return redirect("users:listar_cartoes")

        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect("users:listar_cartoes")

    return render(request, "users/perfil/cliente/listar_cartoes.html", {
        "user": cliente,
        "cartoes": Cartao.objects.all(),
    })

def meus_cartoes(request):
    # Garante que o usuário está logado e é um cliente
    if "user_id" not in request.session:
        return redirect("users:login")

    admUser = request.session.get("admUser", False)
    if admUser:
        messages.error(request, "Apenas clientes podem visualizar seus cartões.")
        return redirect("users:perfil")

    # Busca o cliente logado
    cliente = get_object_or_404(Cliente, id=request.session["user_id"])

    # Busca os cartões conforme o status
    cartoes_pendentes = CartaoCliente.objects.filter(cliente=cliente, status="pendente")
    cartoes_aprovados = CartaoCliente.objects.filter(cliente=cliente, status="aprovado")
    cartoes_negados = CartaoCliente.objects.filter(cliente=cliente, status="negado")

    context = {
        "cliente": cliente,
        "cartoes_pendentes": cartoes_pendentes,
        "cartoes_aprovados": cartoes_aprovados,
        "cartoes_negados": cartoes_negados,
    }

    return render(request, "users/perfil/cliente/meus_cartoes.html", context)

from django.shortcuts import render, redirect
from django.contrib import messages
from users.models import CartaoCliente, Gerente

def visualizar_solicitacoes_cartoes(request):
    # Garante que o gerente está logado
    if "user_id" not in request.session or not request.session.get("admUser", False):
        messages.error(request, "Apenas gerentes podem acessar esta página.")
        return redirect("users:login")

    gerente_id = request.session["user_id"]

    try:
        gerente = Gerente.objects.get(id=gerente_id)
    except Gerente.DoesNotExist:
        messages.error(request, "Gerente não encontrado.")
        return redirect("users:login")

    # Pega TODAS as solicitações de cartões de clientes desse gerente
    solicitacoes = CartaoCliente.objects.filter(
        cliente__gerente_responsavel=gerente
    ).select_related("cliente", "cartao").order_by("-data_solicitacao")

    context = {
        "gerente": gerente,
        "solicitacoes": solicitacoes,
    }
    return render(request, "users/perfil/gerente/solicitacoes_cartoes.html", context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.models import CartaoCliente, Gerente

def aprovar_ou_negar_cartao(request, solicitacao_id, acao):
    # Verifica se o gerente está logado
    if "user_id" not in request.session or not request.session.get("admUser", False):
        messages.error(request, "Apenas gerentes podem realizar essa ação.")
        return redirect("users:login")

    gerente_id = request.session["user_id"]
    solicitacao = get_object_or_404(CartaoCliente, id=solicitacao_id, cliente__gerente_responsavel_id=gerente_id)

    if acao not in ["aprovar", "negar"]:
        messages.error(request, "Ação inválida.")
        return redirect("perfil:solicitacoes_cartoes")

    if solicitacao.status != "pendente":
        messages.warning(request, f"Essa solicitação já foi {solicitacao.status}.")
        return redirect("perfil:solicitacoes_cartoes")

    # Atualiza status
    if acao == "aprovar":
        solicitacao.status = "aprovado"
        solicitacao.resposta_gerente = "Solicitação aprovada pelo gerente."
    else:
        solicitacao.status = "negado"
        solicitacao.resposta_gerente = "Solicitação negada pelo gerente."

    solicitacao.gerente_id = gerente_id
    solicitacao.save()
    messages.success(request, f"Solicitação {acao}ada com sucesso!")
    return redirect("users:solicitacoes_cartoes")
