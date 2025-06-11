from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from  . models  import UserAdmin,  CategoriaProduct, LinksProduct,SubCategoriaProduct,Market
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
    categoria_nome = request.GET.get("categoria")
    subcategoria_nome = request.GET.get("scategoria")
    order = request.GET.get("order")  # 'asc' ou 'desc'
    valor_max = request.GET.get("valor_max")  # novo filtro valor máximo

    categorias = CategoriaProduct.objects.all()
    cdgmk = Market.objects.all()
    subcategorias = SubCategoriaProduct.objects.none()
    produtos = LinksProduct.objects.none()

    if categoria_nome:
        produtos_filtrados = LinksProduct.objects.filter(categoria__categoria=categoria_nome)
        subcategoria_nomes = produtos_filtrados.values_list('subicategoria__subcategoria', flat=True).distinct()
        subcategorias = SubCategoriaProduct.objects.filter(subcategoria__in=subcategoria_nomes)

        if subcategoria_nome:
            produtos = produtos_filtrados.filter(subicategoria__subcategoria=subcategoria_nome)
        else:
            produtos = produtos_filtrados
    else:
        produtos = LinksProduct.objects.all()

    # filtro valor máximo
    if valor_max:
        try:
            valor_max_float = float(valor_max)
            produtos = produtos.filter(preco__lte=valor_max_float)
        except ValueError:
            pass  # ignora filtro se inválido

    # ordenação
    if order == 'asc':
        produtos = produtos.order_by('preco')
    elif order == 'desc':
        produtos = produtos.order_by('-preco')

    return render(request, "index.html", {
        "categorias": categorias,
        "cdgmk": cdgmk,
        "subcategorias": subcategorias,
        "produtos": produtos,
        "categoria_selecionada": categoria_nome,
        "scategoria_selecionada": subcategoria_nome,
        "order": order,
        "valor_max": valor_max,  # envia para o template
    })

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

    nome_categoria = request.GET.get("categoria")
    nome_subcategoria = request.GET.get("scategoria")

    # Base: produtos do usuário
    produtos_qs = LinksProduct.objects.filter(id_user=id_user)

    # Filtra por nome da categoria
    if nome_categoria:
        produtos_qs = produtos_qs.filter(categoria__categoria=nome_categoria)

    # Filtra por nome da subcategoria
    if nome_subcategoria:
        produtos_qs = produtos_qs.filter(subicategoria__subcategoria=nome_subcategoria)

    # Prefetch produtos filtrados para cada categoria
    categorias = CategoriaProduct.objects.prefetch_related(
        Prefetch('produtos', queryset=produtos_qs, to_attr='produtos_usuario')
    )

    # Subcategorias relacionadas aos produtos com base no nome da categoria
    if nome_categoria:
        subcategorias = SubCategoriaProduct.objects.filter(
            id__in=LinksProduct.objects.filter(
                categoria__categoria=nome_categoria
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
            "categoria_selecionada": nome_categoria,
            "scategoria_selecionada": nome_subcategoria,
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
    markets = Market.objects.all()  # Aqui puxa todas as lojas
    return render(
        request,
        "links_cadastro.html",
        {
            "nome": nome,
            "id": id,
            "categorias": categorias,
            "subcategorias": subcategorias,
            "markets": markets,  # passa para o template
        },
    )
@never_cache
 

def Cadlink(request):
    if request.method == "POST":
        iduser = request.POST.get("id-user")
        nome_produto = request.POST.get("nome-produto")
        fabricante = request.POST.get("fabricante")
        link = request.POST.get("link")
        categoriapro_id = request.POST.get("categoriapro")
        scategoriapro_id = request.POST.get("subcategoriapro")
        market_id = request.POST.get("market")  # novo campo para loja
        descricao = request.POST.get("descricao")
        midia = request.POST.get("midia")
        preco = request.POST.get("preco")
        
        codigo = gerar_codigo_unico()
        
        # Busca a categoria e subcategoria pelo id
        try:
            categoria_obj = CategoriaProduct.objects.get(categoria=categoriapro_id)
            subcat_obj = SubCategoriaProduct.objects.get(subcategoria=scategoriapro_id)
        except CategoriaProduct.DoesNotExist:
            messages.error(request, "Categoria inválida.")
            return redirect('link_cadastro')
        
        # Busca o Market (loja) pelo id, se enviado
        market_obj = None
        if market_id:
            try:
                market_obj = Market.objects.get(id=market_id)
            except Market.DoesNotExist:
                messages.warning(request, "Loja inválida, ignorando.")
        
        # Cria o produto, incluindo o market_obj (que pode ser None)
        LinksProduct.objects.create(
            id_user=iduser,
            nomepro=nome_produto,
            links=link,
            categoria=categoria_obj,
            subicategoria=subcat_obj,
            market=market_obj,
            descricao=descricao,
            midia=midia,
            preco=preco,
            codigo=codigo,
            fabricante=fabricante or "Desconhecido",
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
        subcategorias = SubCategoriaProduct.objects.all()
        mercados = Market.objects.all()  # <-- ADICIONADO AQUI

        return render(request, "editar_produto.html", {
            "produto": produto,
            "categorias": categorias,
            "subcategorias": subcategorias,
            "mercados": mercados,  # <-- ADICIONADO AQUI
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
        produto.fabricante = request.POST.get("fabricante") or "Desconhecido"
        produto.categoria_id = request.POST.get("categoria_id")
        produto.subicategoria_id = request.POST.get("subcategoria_id")

        market_id = request.POST.get("market_id")  # captura o id da loja

        if market_id:
            try:
                produto.market = Market.objects.get(id=market_id)
            except Market.DoesNotExist:
                produto.market = None
        else:
            produto.market = None

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
            categoria = get_object_or_404(CategoriaProduct, categoria=catid)
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
            subcategoria= get_object_or_404(SubCategoriaProduct, subcategoria=scatid)
            subcategoria.delete()
            messages.success(request, "subcategoria deletada com sucesso.")
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

    categoria_nome = request.GET.get("categoria")
    subcategoria_nome = request.GET.get("scategoria")
    valor_max = request.GET.get("valor_max")  # novo filtro valor máximo

    categorias = CategoriaProduct.objects.all()
    cdgmk = Market.objects.all()  # garantir que sempre exista

    subcategorias = SubCategoriaProduct.objects.none()
    produtos = LinksProduct.objects.none()

    if categoria_nome:
        produtos_filtrados = LinksProduct.objects.filter(categoria__categoria=categoria_nome).select_related('market')
        
        subcategoria_ids = produtos_filtrados.values_list('subicategoria_id', flat=True).distinct()
        subcategorias = SubCategoriaProduct.objects.filter(id__in=subcategoria_ids)

        if subcategoria_nome:
            produtos = produtos_filtrados.filter(subicategoria__subcategoria=subcategoria_nome)
        else:
            produtos = produtos_filtrados

        # filtro valor máximo
        if valor_max:
            try:
                valor_max_float = float(valor_max)
                produtos = produtos.filter(preco__lte=valor_max_float)
            except ValueError:
                pass  # valor inválido, ignora o filtro

    if codigo:
        try:
            produto = LinksProduct.objects.select_related('market').get(codigo=codigo)
        except LinksProduct.DoesNotExist:
            produto = None

    return render(request, "index.html", {
        "cdgmk": cdgmk,
        "produto": produto,
        "codigo": codigo,
        "categorias": categorias,
        "subcategorias": subcategorias,
        "produtos": produtos,
        "categoria_selecionada": categoria_nome,
        "scategoria_selecionada": subcategoria_nome,
        "valor_max": valor_max,  # envia para o template
    })
