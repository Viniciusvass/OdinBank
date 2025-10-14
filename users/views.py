from django.shortcuts import redirect, render
from .models import Cliente, Gerente
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db.models import Sum

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
