from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from . models import UserAdmin
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache
from django.utils import timezone
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

def index(request):
   return render(request, "index.html")


def admin_site(request):
    return render(request,'admin.html')
   
"""   context = {}

msg = '''
<h2>Olá, este é um e-mail de teste</h2>
<p>Enviado automaticamente ao acessar a página.</p>
<button style="padding: 10px; background-color: #4CAF50; color: white;">Clique aqui</button>
'''

try:
    send_mail(
        'Teste automático',
        '',  # corpo texto simples vazio
        settings.EMAIL_HOST_USER,
        ['leo89stg@gmail.com'],
        html_message=msg,
        fail_silently=False
    )
    context['result'] = 'Email enviado automaticamente.'
except Exception as e:
    context['result'] = f'Erro ao enviar email: {e}'

return render(request, "index.html", context) """

def new_user(request):
    return render(request,'account_new.html')



@csrf_exempt
def CreateUser(request):
    
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email=request.POST.get("email", "").strip()
        senha=request.POST.get("senha", "").strip()
        senharepetida=request.POST.get("senharepetida", "").strip()
        Rede_social=request.POST.get("Rede_social", "").strip()
        if senha != senharepetida:
            return render(request, 'account_new.html', {'wrn': 'senhas são diferentes'})
        if not nome or not email or not senha:
            return render(request, 'account_new.html', {'wrn': 'Preencha todos os campos corretamente.'})

        # Verifica se já existe um usuário com esse e-mail
        if UserAdmin.objects.filter(email=email).exists():
            return render(request, 'account_new.html', {'wrn': 'Este e-mail já está em uso.'})   
        senha_hash = make_password(senha)
        usuario = UserAdmin(nome=nome, email=email, senha=senha_hash, Rede_social=Rede_social)

        try:
            usuario.save()
            return render(request, 'account_new.html', {'Ok': 'Cadastro realizado com sucesso!'})
        except Exception as e:
            return render(request, 'account_new.html', {'erro': 'Erro ao salvar o usuário.'}) 
 # Se for GET, exibe o formulário de cadastro (ou qualquer outra coisa)
    return render(request, "account_new.html")

def login(request):
    
        if request.method == "POST":
            email = request.POST.get("email")
            senha = request.POST.get("senha")
            try :
                admin = UserAdmin.objects.get(email=email )
                if check_password(senha , admin.senha):
                    request.session['nome'] = admin.nome
                    request.session['id'] =  admin.id
                    request.session['created_at'] =admin.created_at.isoformat()
                    return redirect('dashboard')  # Rota protegida
                else:
                  return render(request, 'admin.html',  {'erro': 'Senha incorreta.'})    
            except UserAdmin.DoesNotExist:
                return render(request, 'admin.html',  {'erro': 'Usário não encontrado'})   
            
        return render(request, 'admin.html')    
            
@never_cache
def dashboard(request):
    if 'id' not in request.session:
        return redirect('admin_site')  # Redireciona para login se não estiver logado
    
    nome = request.session.get('nome')
    id = request.session.get('id')
   # data_str= request.session.get('created_at')
    return render(request, 'painel.html', {'nome': nome ,'id':id })
    
    
def logout(request):
    request.session.flush()  # Limpa todos os dados da sessão
    return redirect('admin_site') 

     