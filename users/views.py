from django.shortcuts import redirect, render
from .models import Cliente, Gerente
from datetime import datetime
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.hashers import check_password

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

    # Se for gerente (admUser=True)
    if admUser:
        user = Gerente.objects.get(id=user_id)
        return render(request, "users/perfil/gerente/index.html", {"user": user})

    # Se for cliente (admUser=False)
    user = Cliente.objects.get(id=user_id)
    return render(request, "users/perfil/cliente/index.html", {"user": user})