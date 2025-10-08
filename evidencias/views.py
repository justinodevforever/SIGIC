# views.py
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
from .models import *
from casos.models import *
from usuario.models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt


@login_required
def create_evidence(request, caso_id):

    caso = Caso.objects.get(id=caso_id)

    users = Usuario.objects.filter(
        cargo__in=['investigador','delegado', 'perito']
    )

    tipos = TipoEvidencia.objects.filter(ativo=True)


    if request.method =='POST':

        form = EvidenciaForm(request.POST, instance=caso)

        context = {
            'form': form,
            'tipos': tipos,
            'users': users,
            'caso': caso
        }
        if form.is_valid():

            ev = form.save()

            LogAuditoria.objects.create(
                usuario=request.user,
                acao='create',
                modelo='Evidencia',
                objeto_id=str(ev.id),
                descricao=f'Evidência criada: {ev.numero_evidencia}',
                ip_origem=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )


            return render(request, 'evidencia/create_evidence.html',context)
        else:
            return render(request, 'evidencia/create_evidence.html',context)

    else:
        form = EvidenciaForm()
        context = {
            'form': form,
            'tipos': tipos,
            'users': users,
            'caso': caso
        }

        return render(request, 'evidencia/create_evidence.html',context)

@login_required
def list_evidence(request):

    if request.method == 'POST':

        numero_evidencia = request.POST['numero_evidencia']
        evidencias = Evidencia.objects.filter(numero_evidencia__icontains=numero_evidencia)

        paginator = Paginator(evidencias, 20)
        page = request.GET.get('page', 1)

        objs = paginator.page(page)

        context={
            'evidencias': objs
        }

        return render(request, 'evidencia/list_evidence.html', context)

    else:

        evidencias = Evidencia.objects.all()

        paginator = Paginator(evidencias, 20)
        page = request.GET.get('page', 1)

        objs = paginator.page(page)

        context={
            'evidencias': objs
        }

        return render(request, 'evidencia/list_evidence.html', context)

@login_required
def detail_evidence(request, id):

    evidencia = Evidencia.objects.prefetch_related('cadeia_custodia').get(id=id)
    mov = CadeiaCustomia.objects.filter(evidencia=evidencia)

    context = {
        'evidencia': evidencia,
        'movimentos': mov
    }
    

    return render(request, 'evidencia/detail_evidence.html', context)

@login_required
@require_http_methods(['POST'])
def get_evidence(request):

    numero_evidencia = request.POST.get('numero_evidencia')
    nu = request.GET

    print(numero_evidencia, nu)

    evidencia = {}

    try:
        evidencia = Evidencia.objects.get(numero_evidencia__icontains=numero_evidencia)
    except Exception as e:
        pass

    context = {
        'numero_evidencia': evidencia.numero_evidencia,
        'id': evidencia.pk
    }
    

    return JsonResponse({'context': context}, safe=False)

@login_required
def edit_evidence(request, id):

    evidencia = Evidencia.objects.get(id=id)
    users = Usuario.objects.filter(
        cargo__in=['investigador','delegado', 'perito']
    )
    evidencia.data_coleta = evidencia.data_coleta.strftime('%Y-%m-%dT%H:%M')

    if request.method == 'POST':
        form = EvidenciaForm(request.POST)

        if form.is_valid():

            ev = form.save(evidencia)

            LogAuditoria.objects.create(
                usuario=request.user,
                acao='update',
                modelo='Evidencia',
                objeto_id=str(ev.id),
                descricao=f'Evidência atualizada: {ev.numero_evidencia}',
                ip_origem=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            messages.success(request, 'Evidência atualizada com sucesso')
            return render(request, 'evidencia/edit_evidence.html', 
            {'form': form, 'evidencia':evidencia, 'users': users})
        else:

            messages.error(request, 'Erro ao atualizar a evidência!')

            return render(request, 'evidencia/edit_evidence.html', 
            {'form': form, 'evidencia':evidencia, 'users': users})
    else:
        form = EvidenciaForm(
            initial={
            'peso': evidencia.peso,
            'valor_estimado': evidencia.valor_estimado
        }
        )

        return render(request, 'evidencia/edit_evidence.html', 
        {'form': form, 'evidencia':evidencia, 'users': users})

@login_required
@require_http_methods(['POST'])
def delete_evidence(request, id):

    ev = Evidencia.objects.get(id=id)

    LogAuditoria.objects.create(
        usuario=request.user,
        acao='delete',
        modelo='Evidencia',
        objeto_id=str(ev.id),
        descricao=f'Evidência eliminada: {ev.numero_evidencia}',
        ip_origem=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    ev.delete()

    return redirect('list_evidence')

@login_required
def create_expertise(request):
    form = PericiaForm()

    if request.method == 'POST':

        form = PericiaForm(request.POST)

        if form.is_valid():

            pericia = form.save()

            pericia.criado_por = request.user

            pericia.save()

            messages.success(request, 'Dados da perícia criado com sucesso')

            return render(request, 'pericia/create_expertise.html', {'form': form})
        else:
            messages.error(request, 'Erro ao salvar Dados da perícia')
            return render(request, 'pericia/create_expertise.html', {'form': form})

    else:
        form = PericiaForm()
        return render(request, 'pericia/create_expertise.html', {'form': form})

@login_required
def edit_expertise(request, id):

    pericia = get_object_or_404(Pericia, id=id)

    form = PericiaForm()

    context={
        'form': form,
        'pericia_id': id,
        'pericia': pericia
    }

    if request.method == 'POST':

        form = PericiaForm(request.POST)
        context={
            'form': form,
            'pericia_id': id,
            'pericia': pericia
        }

        if form.is_valid():

            pericia = form.save(pericia=pericia)

            pericia.save()

            return render(request, 'pericia/edit_expertise.html', context)
        else:
            messages.error(request, 'Erro ao salvar Dados da perícia')
            return render(request, 'pericia/edit_expertise.html', context)

    else:
        return render(request, 'pericia/edit_expertise.html', context)

@login_required
def list_evidence_expertise(request):

    tipo = request.GET.get('tipo')
    numero_evidencia = request.GET.get('numero_evidencia')
    pericas = Pericia.objects.all().order_by('-data_criacao')

    if numero_evidencia:

        pericas = Pericia.objects.filter(evindecia__numero_evidencia__icontains=numero_evidencia)

    if tipo:
        pericas = Pericia.objects.filter(tipo__icontains=tipo)

    for p in pericas:
        if len(p.conclusao) > 20:
            p.conclusao = f'{p.conclusao[:20]}...'

        if len(p.resultado) > 20:
            p.resultado = f'{p.resultado[:20]}...'

    paginator = Paginator(pericas, 20)
    page = request.GET.get('page', 1)

    objs = paginator.page(page)

    context={
        'pericias': objs
    }

    return render(request, 'pericia/list_evidence_expertise.html', context)

@login_required
@require_http_methods(['POST'])
def delete_expertise(request, id):

    pericia = Pericia.objects.get(id=id)

    pericia.delete()

    return redirect('list_evidence_expertise')

def detail_expertise(request, id):

    pericia = Pericia.objects.get(id=id)

    return render(request, 'pericia/detail_expertise.html', {'pericia': pericia})

@login_required
def moviment_evidence(request, id):

    evidencia = Evidencia.objects.get(id=id)
    users = Usuario.objects.filter(
        cargo__in=['investigador','delegado', 'perito']
    )

    if request.method == 'POST':

        form = CadeiaCustodiaForm(request.POST, instance=evidencia)
        context = {
            'users': users,
            'evidencia': evidencia,
            'form': form
        }

        if form.is_valid():

            mov = form.save()
            anterior = {
                'evidencia': {
                    'numero_evidencia': mov.evidencia.numero_evidencia
                },
                'tipo_movimentacao':mov.tipo_movimentacao,
                'local_destino':mov.local_destino,
                'local_origem':mov.local_origem,
                'responsavel_anterior':{
                    'ultimo_nome':mov.responsavel_anterior.last_name
                    },
                'responsavel_atual':{
                    'ultimo_nome': mov.responsavel_atual.last_name
                    },
                'motivo':mov.motivo,
                'observacoes':mov.observacoes,
            }
            LogAuditoria.objects.create(
                usuario=request.user,
                acao='create',
                modelo='CadeiaCustomia',
                objeto_id=str(mov.id),
                descricao=f'Cadeia custódia criada ou movimentação feita: {mov.get_tipo_movimentacao_display}',
                ip_origem=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                dados_anteriores = anterior,
                dados_novos = anterior
            )
            messages.success(request, 'Movimentação de evidência feita com sucesso!')
            return render(request, 'evidencia/moviment.html', context)
        else:
            messages.success(request, 'Erro ao fazer movimentação de evidência!')
            return render(request, 'evidencia/moviment.html', context)
    else:
        form = CadeiaCustodiaForm()
        context = {
            'users': users,
            'evidencia': evidencia,
            'form': form
        }

        return render(request, 'evidencia/moviment.html', context)

class evidenciaListView(LoginRequiredMixin, ListView):
    
    model = Evidencia
    template_name = 'investigation/evidencia_list.html'
    context_object_name = 'evidencias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Evidencia.objects.select_related(
            'caso', 'tipo', 'coletado_por', 'custodia_atual'
        )
        
        # filtros
        status = self.request.get.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        caso_id = self.request.get.get('caso')
        if caso_id:
            queryset = queryset.filter(caso_id=caso_id)
        
        # busca
        search = self.request.get.get('search')
        if search:
            queryset = queryset.filter(
                Q(numero_evidencia__icontains=search) |
                Q(descricao__icontains=search) |
                Q(caso__numero_caso__icontains=search)
            )
        
        return queryset.order_by('-data_coleta')

class evidenciaDetailView(LoginRequiredMixin, DetailView):
    
    model = Evidencia
    template_name = 'investigation/evidencia_detail.html'
    context_object_name = 'Evidencia'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        evidencia = self.object
        
        # cadeia de custódia
        context['cadeia_custodia'] = Evidencia.cadeia_custodia.all().order_by('-data_movimentacao')
        
        # arquivos relacionados
        context['arquivos'] = Evidencia.arquivos.all().order_by('-data_upload')
        
        return context

@login_required
def upload_arquivo(request, caso_id):
    
    caso = get_object_or_404(Caso, pk=caso_id)
    
    if request.method == 'post':
        form = ArquivoForm(request.post, request.files)
        if form.is_valid():
            arquivo = form.save(commit=False)
            arquivo.caso = caso
            arquivo.uploadado_por = request.user
            arquivo.save()
            
            messages.success(request, 'arquivo enviado com sucesso!')
            return redirect('caso_detail', pk=caso.pk)
    else:
        form = ArquivoForm()
    
    return render(request, 'investigation/upload_arquivo.html', {
        'form': form,
        'caso': caso
    })


