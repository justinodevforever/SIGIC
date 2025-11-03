from django.shortcuts import render
from usuario.models import *
from django.core.paginator import Paginator

def confg(request):


    return render(request, 'configuracoes.html')

def secao_geral(request):

    return render(request, 'secao_geral.html')

def secao_notificacao(request):

    return render(request, 'secao_notificacao.html')

def secao_relatorio(request):

    return render(request, 'secao_relatorio.html')

def secao_sistema(request):

    return render(request, 'secao_sistema.html')

def secao_seguranca(request):

    return render(request, 'secao_seguranca.html')

def secao_usuario(request):

    return render(request, 'secao_usuario.html')

def logs_auditorio(request):

    auditorias = LogAuditoria.objects.all().order_by('-data_acao')
    
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 10)
    tipo = request.POST.get('tipo')

    if request.POST:

        auditorias = LogAuditoria.objects.filter(acao=tipo)


    paginator = Paginator(auditorias, per_page)

    obj = paginator.page(page)

    context = {
        'auditorias': obj,
        'per_page': per_page
    }

    return render(request, 'logs/logs_auditorio.html', context)

def detail_aditorio(request, id):

    auditoria = LogAuditoria.objects.get(id=id)


    return render(request, 'logs/detail_auditoria.html', {'auditoria': auditoria})