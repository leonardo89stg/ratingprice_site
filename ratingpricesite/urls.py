from django.urls import path
from django.http import HttpResponse
from . import views
from django.contrib.auth import views as auth_views
 
from django.urls import path
urlpatterns = [
    path("", views.index, name="index"),
    path("/admin_site", views.admin_site, name="admin_site"),
]