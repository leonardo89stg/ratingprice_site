from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from  . models  import UserAdmin,  CategoriaProduct, LinksProduct,SubCategoriaProduct
from django.db.models import Prefetch
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import get_object_or_404
import certifi
import os
import random
import string

os.environ["SSL_CERT_FILE"] = certifi.where()


def gerar_codigo_unico(tamanho=6):
    caracteres = string.ascii_uppercase + string.digits  # Letras maiúsculas + dígitos 0-9
    codigo = ''.join(random.choices(caracteres, k=tamanho))
    return codigo
def index(request):
    categoria_id = request.GET.get("categoria")
    subcategoria_id = request.GET.get("scategoria")

    categorias = CategoriaProduct.objects.all()

    if categoria_id:
        produtos_filtrados = LinksProduct.objects.filter(categoria_id=categoria_id)
        subcategoria_ids = produtos_filtrados.values_list('subicategoria_id', flat=True).distinct()
        subcategorias = SubCategoriaProduct.objects.filter(id__in=subcategoria_ids)
    else:
        subcategorias = SubCategoriaProduct.objects.all()

    produtos = LinksProduct.objects.all()

    if categoria_id:
        produtos = produtos.filter(categoria_id=categoria_id)
    if subcategoria_id:
        produtos = produtos.filter(subicategoria_id=subcategoria_id)

    return render(
        request,
        "index.html",
        {
            "categorias": categorias,
            "subcategorias": subcategorias,
            "produtos": produtos,
            "categoria_selecionada": categoria_id,
            "scategoria_selecionada": subcategoria_id,
        },
    )
def admin_site(request):
    return render(request, "admin.html")


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
    return render(request, "account_new.html")


@csrf_exempt
def CreateUser(request):

    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        senha = request.POST.get("senha", "").strip()
        senharepetida = request.POST.get("senharepetida", "").strip()
        Rede_social = request.POST.get("Rede_social", "").strip()
        if senha != senharepetida:
            return render(request, "account_new.html", {"wrn": "senhas são diferentes"})
        if not nome or not email or not senha:
            return render(
                request,
                "account_new.html",
                {"wrn": "Preencha todos os campos corretamente."},
            )

        # Verifica se já existe um usuário com esse e-mail
        if UserAdmin.objects.filter(email=email).exists():
            return render(
                request, "account_new.html", {"wrn": "Este e-mail já está em uso."}
            )
        senha_hash = make_password(senha)
        usuario = UserAdmin(
            nome=nome, email=email, senha=senha_hash, Rede_social=Rede_social
        )

        try:
            usuario.save()
            return render(
                request, "account_new.html", {"Ok": "Cadastro realizado com sucesso!"}
            )
        except Exception as e:
            return render(
                request, "account_new.html", {"erro": "Erro ao salvar o usuário."}
            )
    # Se for GET, exibe o formulário de cadastro (ou qualquer outra coisa)
    return render(request, "account_new.html")


def login(request):

    if request.method == "POST":
        email = request.POST.get("email")
        senha = request.POST.get("senha")
        try:
            admin = UserAdmin.objects.get(email=email)
            if check_password(senha, admin.senha):
                request.session["nome"] = admin.nome
                request.session["id"] = admin.id
                request.session["created_at"] = admin.created_at.isoformat()
                return redirect("dashboard")  # Rota protegida
            else:
                return render(request, "admin.html", {"erro": "Senha incorreta."})
        except UserAdmin.DoesNotExist:
            return render(request, "admin.html", {"erro": "Usário não encontrado"})

    return render(request, "admin.html")


@never_cache
def dashboard(request):
    if "id" not in request.session:
        return redirect("admin_site")

    id_user = request.session.get("id")
    nome = request.session.get("nome")

    categoria_selecionada = request.GET.get("categoria")
    scategoria_selecionada = request.GET.get("scategoria")

    # Base: produtos do usuário
    produtos_qs = LinksProduct.objects.filter(id_user=id_user)

    # Filtra por categoria se selecionada
    if categoria_selecionada:
        produtos_qs = produtos_qs.filter(categoria_id=categoria_selecionada)

    # Filtra por subcategoria se selecionada
    if scategoria_selecionada:
        produtos_qs = produtos_qs.filter(subicategoria_id=scategoria_selecionada)

    # Prefetch produtos filtrados para cada categoria
    categorias = CategoriaProduct.objects.prefetch_related(
        Prefetch('produtos', queryset=produtos_qs, to_attr='produtos_usuario')
    )

    # Filtra subcategorias que aparecem nos produtos da categoria selecionada
    if categoria_selecionada:
        subcategorias = SubCategoriaProduct.objects.filter(
            id__in=LinksProduct.objects.filter(
                categoria_id=categoria_selecionada
            ).values_list('subicategoria_id', flat=True).distinct()
        )
    else:
        subcategorias = SubCategoriaProduct.objects.all()

    return render(
        request,
        "painel.html",
        {
            "nome": nome,
            "categorias": categorias,
            "subcategorias": subcategorias,
            "categoria_selecionada": categoria_selecionada,
            "scategoria_selecionada": scategoria_selecionada,
        },
    )

@never_cache
def lnk_cadastro(request):
    if "id" not in request.session:
        return redirect("admin_site")  # Redireciona para login se não estiver logado

    nome = request.session.get("nome")
    id = request.session.get("id")
    # data_str= request.session.get('created_at')

    categorias = CategoriaProduct.objects.filter( )
    subcategorias = SubCategoriaProduct.objects.filter()
    return render(
        request,
        "links_cadastro.html",
        {"nome": nome, "id": id, "categorias": categorias ,"subcategorias": subcategorias   },
    )


@never_cache
 

def Cadlink(request):
    if request.method == "POST":
        iduser = request.POST.get("id-user")
        nome_produto = request.POST.get("nome-produto")
        link = request.POST.get("link")
        categoriapro_id = request.POST.get("categoriapro")
        scategoriapro_id = request.POST.get("subcategoriapro")
        descricao = request.POST.get("descricao")
        midia = request.POST.get("midia")
        preco = request.POST.get("preco")
        
        codigo = gerar_codigo_unico()
        
        # Busca a categoria correta pelo id
        try:
            categoria_obj = CategoriaProduct.objects.get(id=categoriapro_id)
            subcat_obj = SubCategoriaProduct.objects.get(id=scategoriapro_id)
        except CategoriaProduct.DoesNotExist:
            messages.error(request, "Categoria inválida.")
            return redirect('link_cadastro')
        
        LinksProduct.objects.create(
            id_user=iduser,
            nomepro=nome_produto,
            links=link,
            categoria=categoria_obj, # Passa a instância da categoria
            subicategoria = subcat_obj ,
            descricao=descricao,
            midia=midia,
            preco=preco,
            codigo=codigo,
            created_at=timezone.now()
        )
        
        messages.success(request, "Produto cadastrado com sucesso!")
        return redirect('link_cadastro')

    return redirect('dashboard')



@never_cache
def deleteproduto(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo") 
        id_user = request.POST.get("id_user")# certifique-se de que o name do input hidden é "codigo"
        try:
            produto = get_object_or_404(LinksProduct, codigo=codigo,id_user=id_user )
            produto.delete()
            messages.success(request, "Produto deletado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao deletar Produto: {str(e)}")
        return redirect('dashboard')

@never_cache
def editarproduto(request):
    if request.method == "GET":
        codigo = request.GET.get("codigo")
        id_user = request.session.get("id")
        nome = request.session.get("nome")
        produto = get_object_or_404(LinksProduct, codigo=codigo, id_user=id_user)
        categorias = CategoriaProduct.objects.all()

        # Corrija aqui para usar o nome correto do campo da FK no model SubCategoriaProduct:
        subcategorias = SubCategoriaProduct.objects.all()

        return render(request, "editar_produto.html", {
            "produto": produto,
            "categorias": categorias,
            "subcategorias": subcategorias,
            "nome": nome
        })

@never_cache
def salvar_edicao(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")
        id_user = request.session.get("id")  # pegar da sessão para segurança

        produto = get_object_or_404(LinksProduct, codigo=codigo, id_user=id_user)

        produto.nomepro = request.POST.get("nomepro")
        produto.preco = request.POST.get("preco")
        produto.descricao = request.POST.get("descricao")
        produto.links = request.POST.get("links")
        produto.midia = request.POST.get("midia")
        produto.categoria_id = request.POST.get("categoria_id")
        produto.subicategoria_id = request.POST.get("subcategoria_id")  # corrigido

        try:
            produto.save()
            messages.success(request, "Produto atualizado com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar o produto: {str(e)}")

        return redirect("dashboard")
@never_cache
def config(request):
    if "id" not in request.session:
        return redirect("admin_site")  # Redireciona para login se não estiver logado

    nome = request.session.get("nome")
    id = request.session.get("id")
    # data_str= request.session.get('created_at')

    categorias = CategoriaProduct.objects.filter()
    subcategorias = SubCategoriaProduct.objects.filter()
    return render(
        request, "config.html", {"nome": nome, "id": id, "categorias": categorias ,"subcategorias": subcategorias}
    )


@never_cache
def cadacateg(request):
    if request.method == "POST":
        
        categ = request.POST.get("categoria", "").strip()

        if not categ:
            messages.warning(request, "Dados em branco, preencha tudo.")
            return redirect("config")

        if CategoriaProduct.objects.filter(categoria=categ).exists():
            messages.warning(request, "Categoria já existe.")
            return redirect("config")

        data_cat = CategoriaProduct(categoria=categ,  )
        try:
            data_cat.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("config")
        except Exception:
            messages.error(request, "Erro ao salvar categoria.")
            return redirect("config")


def delcatg(request):
    if request.method == "POST":
        catid = request.POST.get("catid")
        print("ID da categoria recebida:", catid)  # Debug
        
        try:
            categoria = get_object_or_404(CategoriaProduct, id=catid)
            categoria.delete()
            messages.success(request, "Categoria deletada com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao deletar categoria: {e}")
    return redirect("config")

@never_cache
def scadacateg(request):
    if request.method == "POST":
        
        categ = request.POST.get("scategoria", "").strip()

        if not categ:
            messages.warning(request, "Dados em branco, preencha tudo.")
            return redirect("config")

        if SubCategoriaProduct.objects.filter(subcategoria=categ).exists():
            messages.warning(request, "Sub Categoria já existe.")
            return redirect("config")

        data_cat = SubCategoriaProduct(subcategoria=categ,  )
        try:
            data_cat.save()
            messages.success(request, "Cadastro realizado com sucesso!")
            return redirect("config")
        except Exception:
            messages.error(request, "Erro ao salvar categoria.")
            return redirect("config")


def sdelcatg(request):
    if request.method == "POST":
        scatid = request.POST.get("scatid")
        print("ID da categoria recebida:", scatid)  # Debug
        
        try:
            categoria = get_object_or_404(SubCategoriaProduct, id=scatid)
            categoria.delete()
            messages.success(request, "Categoria deletada com sucesso.")
        except Exception as e:
            messages.error(request, f"Erro ao deletar categoria: {e}")
    return redirect("config")

def logout(request):
    request.session.flush()  # Limpa todos os dados da sessão
    return redirect("admin_site")
'''
parte de busca

'''

def buscar_produto(request):
    codigo = request.GET.get("codigo", "").strip()
    produto = None

    if codigo:
        try:
            produto = LinksProduct.objects.get(codigo=codigo)
        except LinksProduct.DoesNotExist:
            produto = None

    return render(request, "index.html", {
        "produto": produto,
        "codigo": codigo
    })