from django.urls import path
from django.http import HttpResponse
from . import views
from django.contrib.auth import views as auth_views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("admin_site/", views.admin_site, name="admin_site"),
    path("nw_user/", views.new_user, name="new_user"),
    path("createuser/", views.CreateUser, name="CreateUser"),
    path("login/", views.login, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout, name="logout"),
    path("config/", views.config, name="config"),
    path("cadacateg/", views.cadacateg, name="cadacateg"),
    path("delcatg/", views.delcatg, name="delcatg"),
    path("scadacateg/", views.scadacateg, name="scadacateg"),
    path("sdelcatg/", views.sdelcatg, name="sdelcatg"),
    
    
    path("link_cadastro/", views.lnk_cadastro, name="link_cadastro"),
    path("Cadlink/", views.Cadlink, name="Cadlink"),
    path("deleteproduto/", views.deleteproduto, name="deleteproduto"),
    path("editarproduto/", views.editarproduto, name="editarproduto"),
    path("salvar_edicao/", views.salvar_edicao, name="salvar_edicao"),
    path("buscar_produto/", views.buscar_produto, name="buscar_produto"),

]
