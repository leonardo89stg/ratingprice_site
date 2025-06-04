from django.shortcuts import render,redirect
from django.http import HttpRequest,HttpResponse
from django.core.mail import send_mail
from django.conf import settings

import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

def index(request):
   return render(request, "index.html")


def admin_site(request):
   
    context = {}

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

    return render(request, "index.html", context)

