from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from evidencias.models import *
from casos.models import *
from usuario.models import *


def home(request):


  return render(request, 'home.html')

@login_required
def dashboard(request):
    
    total_casos = Caso.objects.filter(ativo=True).count()
    casos_abertos = Caso.objects.filter(status__in=['aberto', 'em_andamento']).count()
    casos_concluido = Caso.objects.filter(status__in=['concluido']).count()
    casos_urgentes = Caso.objects.filter(prioridade__gte=4, status__in=['aberto', 'em_andamento']).count()
    total_evidencias = Evidencia.objects.count()
    
    meus_casos = Caso.objects.filter(
        Q(investigador_principal=request.user) | 
        Q(investigadores_apoio=request.user)
    ).distinct()[:5]

    casos_recentes = Caso.objects.filter()[:10]
    
    prazo_limite = datetime.now() + timedelta(days=7)

    casos_prazo = Caso.objects.filter(
        prazo_conclusao__lte=prazo_limite,
        status__in=['aberto', 'em_andamento']
    )[:5]
    
    evidencias_pendentes = Evidencia.objects.filter(
        status='em_analise',
        custodia_atual=request.user
    )[:5]

    eventos_recentes = EventoTimeline.objects.filter(
        caso__in=meus_casos
    ).order_by('-data_criacao')[:10]
    
    
    context = {
        'total_casos': total_casos,
        'casos_concluido': casos_concluido,
        'casos_abertos': casos_abertos,
        'casos_urgentes': casos_urgentes,
        'total_evidencias': total_evidencias,
        'meus_casos': meus_casos,
        'casos_prazo': casos_prazo,
        'evidencias_pendentes': evidencias_pendentes,
        'eventos_recentes': eventos_recentes,
        'casos_recentes': casos_recentes,
    }
    
    return render(request, 'dashboard.html', context)
