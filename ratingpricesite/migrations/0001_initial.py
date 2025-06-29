# Generated by Django 5.2.1 on 2025-06-09 15:52

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriaProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categoria', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='SubCategoriaProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subcategoria', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='UserAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('email', models.CharField(blank=True, max_length=50, unique=True)),
                ('senha', models.CharField(max_length=30)),
                ('Rede_social', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='LinksProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_user', models.TextField()),
                ('links', models.URLField()),
                ('nomepro', models.TextField(default='Sem nome')),
                ('descricao', models.TextField()),
                ('midia', models.URLField()),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10)),
                ('codigo', models.CharField(default='000000', max_length=6)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('categoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos', to='ratingpricesite.categoriaproduct')),
                ('subicategoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='produtos', to='ratingpricesite.subcategoriaproduct')),
            ],
        ),
    ]
