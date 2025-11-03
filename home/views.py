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
from django.db.models.functions import ExtractMonth


def home(request):


  return render(request, 'home.html')

def perfil(request):
    user = Usuario.objects.get(id=request.user.id)

    context = {
        'user': user
    }
    print(user.data_nascimento)

    return render(request, 'perfil.html', context)

@login_required
def dashboard(request):

     # --- Lista de meses em português ---
    meses_pt = [
        '',  # índice 0 não usado (meses começam em 1)
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ]
    
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
    

    casos_status = (
        Caso.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )
    labels_status = [c['status'].capitalize() for c in casos_status]
    dados_status = [c['total'] for c in casos_status]

    # Contagem de casos por prioridade
    casos_prioridade = (
        Caso.objects.values('prioridade')
        .annotate(total=Count('id'))
        .order_by('prioridade')
    )
    labels_prioridade = [
        dict(Caso.PRIORIDADE_CHOICES).get(c['prioridade'])
        for c in casos_prioridade
    ]
    dados_prioridade = [c['total'] for c in casos_prioridade]

    # Contagem de casos por tipo de crime
    casos_tipo = (
        Caso.objects.values('tipo_crime__nome')  # supondo que TipoCrime tem campo 'nome'
        .annotate(total=Count('id'))
        .order_by('tipo_crime__nome')
    )
    labels_tipo = [c['tipo_crime__nome'] for c in casos_tipo]
    dados_tipo = [c['total'] for c in casos_tipo]

    # --- Gráfico 4: Casos por Mês ---
    casos_mes = (
        Caso.objects.annotate(mes=ExtractMonth('data_abertura'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    labels_mes = [meses_pt[c['mes']] for c in casos_mes if c['mes']]
    dados_mes = [c['total'] for c in casos_mes]

    context = {
       'labels_mes': labels_mes,
        'dados_mes': dados_mes,
       'labels_status': labels_status,
        'dados_status': dados_status,
        'labels_prioridade': labels_prioridade,
        'dados_prioridade': dados_prioridade,
        'labels_tipo': labels_tipo,
        'dados_tipo': dados_tipo,
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
