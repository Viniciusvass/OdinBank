from django.shortcuts import redirect, render
from .models import User
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
        data_de_nascimento = datetime.strptime(data_str, "%Y-%m-%d").date()
        
        telefone = request.POST.get('telefone')
        tipo_de_conta = request.POST.get('tipo_de_conta')
        admUser = request.POST.get('admUser', 'false') == 'true'

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado!')
            return render(request, 'users/cadastro/index.html')

        if User.objects.filter(cpf=cpf).exists():
            messages.error(request, 'Este CPF já está cadastrado!')
            return render(request, 'users/cadastro/index.html')

        new_user = User(
            cpf=cpf,
            username=username,
            email=email,
            password=password,
            data_de_nascimento=data_de_nascimento,
            telefone=telefone,
            tipo_de_conta=tipo_de_conta,
            admUser=admUser
        )
        new_user.save()
        return redirect('users:login')

    return render(request, 'users/cadastro/index.html')

def view_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
            
            # Aqui é a única alteração: checar senha hash
            if check_password(password, user.password):
                request.session["user_id"] = user.id  # guarda na sessão
                return redirect("users:perfil")
            else:
                return render(request, "users/login/index.html", {"error": "Usuário ou senha inválidos"})

        except User.DoesNotExist:
            return render(request, "users/login/index.html", {"error": "Usuário ou senha inválidos"})

    return render(request, "users/login/index.html")

def view_perfil(request):
    if "user_id" not in request.session:
        return redirect("users:login")

    user = User.objects.get(id=request.session["user_id"])

    # Se for gerente/adm vai pra tela de gerente
    if user.admUser:  
        return render(request, "users/perfil/gerente/index.html", {"user": user})
    
    # Se for cliente vai pra tela de cliente
    return render(request, "users/perfil/cliente/index.html", {"user": user})
