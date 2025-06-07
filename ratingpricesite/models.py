from django.db import models
from django.utils import timezone

# Create your models here.

class UserAdmin(models.Model):
    nome = models.CharField(max_length=200)  # nome do usuário
    email = models.CharField(max_length=50, unique=True , blank=True)
    senha = models.CharField(max_length=30)  # aumente para 255 ou mais
    Rede_social = models.CharField(max_length=255)  # nome do usuário
    created_at = models.DateTimeField(default=timezone.now)
        