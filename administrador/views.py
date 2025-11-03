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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from .models import *
from casos.models import *
from usuario.models import *
from .forms import *
import json
from django.core import serializers



class pessoaListView(LoginRequiredMixin, ListView):
    
    model = Pessoa
    template_name = 'investigation/pessoa_list.html'
    context_object_name = 'pessoas'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Pessoa.objects.filter(ativo=True).prefetch_related(
            'aliases', 'enderecos', 'envolvimentos__caso'
        )
        
        # busca
        search = self.request.get.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_completo__icontains=search) |
                Q(nome_social__icontains=search) |
                Q(cpf__icontains=search) |
                Q(aliases__nome_alias__icontains=search)
            ).distinct()
        
        return queryset.order_by('nome_completo')

class pessoaDetailView(LoginRequiredMixin, DetailView):
    
    model = Pessoa
    template_name = 'investigation/pessoa_detail.html'
    context_object_name = 'pessoa'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pessoa = self.object
        
        # envolvimentos em casos
        context['envolvimentos'] = pessoa.envolvimentos.filter(ativo=True).select_related('caso')
        
        # endereços
        context['enderecos'] = pessoa.enderecos.filter(ativo=True).order_by('-data_criacao')
        
        # aliases
        context['aliases'] = pessoa.aliases.all().order_by('-data_criacao')
        
        return context
    

@require_http_methods(["get"])
def buscar_pessoas(request):
    
    term = request.get.get('term', '')
    if len(term) < 2:
        return JsonResponse({'results': []})
    
    pessoas = Pessoa.objects.filter(
        Q(nome_completo__icontains=term) |
        Q(nome_social__icontains=term) |
        Q(cpf__icontains=term),
        ativo=True
    )[:10]
    
    results = []
    for pessoa in pessoas:
        results.append({
            'id': pessoa.id,
            'text': pessoa.nome_completo,
            'cpf': pessoa.cpf or '',
            'data_nascimento': pessoa.data_nascimento.strftime('%d/%m/%y') if pessoa.data_nascimento else ''
        })
    
    return JsonResponse({'results': results})

@login_required
def create_user(request):

    if request.method == 'POST':

        form = UserForm(request.POST)

        if form.is_valid():

            user = form.save()

            LogAuditoria.objects.create(
                usuario=request.user,
                acao='create',
                modelo='Usuaurio',
                objeto_id=str(user.id),
                descricao=f'Usuário criado: {user.get_full_name}',
                ip_origem=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            return render(request, 'usuario/criar_usuario.html', {'form': form,
            'sucesso': 'Usuário criado com sucesso!'})
        else:

            return render(request, 'usuario/criar_usuario.html', {'form': form,
            'erro': 'Erro ao criar Usuário!'})
        
    else:
        form = UserForm()

        return render(request, 'usuario/criar_usuario.html', {'form': form})

@login_required
def edit_user(request, id):

    user = Usuario.objects.get(id=id)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)

        
        dados_anteriores = serializers.serialize('json', [user]),
        

        if form.is_valid():

            userExist = Usuario.objects.get(username=form.cleaned_data['username'])
            if user.id != userExist.id:


                form.add_error('username', 'Esse nome do usuário já existe!')

                return render(request, 'usuario/edit_user.html', 
                {'user': user, 'form': form})


            usuario = form.save()            
            
            LogAuditoria.objects.create(
                usuario=request.user,
                acao='update',
                modelo='Usuaurio',
                objeto_id=str(usuario.id),
                descricao=f'Usuário Atualizado: {usuario.get_full_name}',
                ip_origem=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                dados_anteriores = dados_anteriores,
                dados_novos = serializers.serialize('json', [usuario])
            )
       
            user.data_nascimento = user.data_nascimento.strftime('%Y-%m-%d')
            return render(request, 'usuario/edit_user.html', 
            {'user': user, 'form': form, 'sucesso': 'Dados do usuário atualizado com sucesso!'})
        
        else:
            user.data_nascimento = user.data_nascimento.strftime('%Y-%m-%d')
            return render(request, 'usuario/edit_user.html', 
            {'user': user, 'form': form, 'erro': 'Erro ao atualizar dados do usuário!'})

    user.data_nascimento = user.data_nascimento.strftime('%Y-%m-%d')
    
    return render(request, 'usuario/edit_user.html', {'user': user})

@login_required
def list_user(request):

    try:
        users = Usuario.objects.all()

        num_page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 20)

        paginator = Paginator(users, per_page)

        objetos = paginator.page(num_page)

    except PageNotAnInteger:

      objetos = paginator.page(1)

    except EmptyPage:
      objetos = paginator.page(paginator.num_pages)

    return render(request, 'usuario/list_user.html', {'users': objetos,'per_page': per_page,})

@login_required
def view_user(request, id):

    user = Usuario.objects.get(id=id)
    return render(request, 'usuario/view_user.html', {'user': user})

@login_required
@require_http_methods(["POST"])
def delete_user(request, id):

    user = Usuario.objects.get(id=id)
    dados = json.loads(request.body)
    password = dados.get('password')
    userLogin = request.user

    if not userLogin.check_password(password.strip()):

        return JsonResponse({'erro': 'Credinciais inválidas'}, status=403)
    
    user.is_active = False
    user.ativo = False
    user.save()
    
    LogAuditoria.objects.create(
        usuario=request.user,
        acao='delete',
        modelo='Usuaurio',
        objeto_id=str(user.id),
        descricao=f'Usuário Desativado do sistema: {user.get_full_name}',
        ip_origem=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return redirect('list_user')
def exe(request):
    
    return render(request, 'exe.html')