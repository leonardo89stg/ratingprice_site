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
   
     
]