from django.db import models
from django.utils import timezone

# Create your models here.

class UserAdmin(models.Model):
    nome = models.CharField(max_length=200)  # nome do usuário
    email = models.CharField(max_length=50, unique=True , blank=True)
    senha = models.CharField(max_length=30)  # aumente para 255 ou mais
    Rede_social = models.CharField(max_length=255)  # nome do usuário
    created_at = models.DateTimeField(default=timezone.now)
    
    
class CategoriaProduct(models.Model):
    categoria = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.categoria
class SubCategoriaProduct(models.Model):
    subcategoria = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.subcategoria
    
class LinksProduct(models.Model):
    id_user = models.TextField()
    links = models.URLField()
    categoria = models.ForeignKey(CategoriaProduct, on_delete=models.CASCADE, related_name='produtos')
    subicategoria =models.ForeignKey(SubCategoriaProduct, on_delete=models.CASCADE, related_name='produtos')
    nomepro = models.TextField(default="Sem nome")
    descricao = models.TextField()
    midia = models.URLField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    codigo = models.CharField(max_length=6, default="000000")
    created_at = models.DateTimeField(default=timezone.now)
