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
from django.core.files.base import ContentFile
from .models import PessoaReconhecimento, HistoricoReconhecimento
from deepface import DeepFace
import base64
import json
import numpy as np
from django.core import serializers

from .models import *
from casos.models import *
from usuario.models import *
from .forms import *
from casos.forms import *
from casos.models import *


def list_researcher(request):
    
    researchers = Usuario.objects.filter(cargo='investigador')
    
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    distintivo = request.GET.get('distintivo')

    if distintivo:
        researchers = Usuario.objects.filter(matricula=distintivo.strip())

    paginator = Paginator(researchers, per_page)

    obj = paginator.page(page)

    context = {
        'researchers': obj,
        'per_page':per_page
    }
    return render(request, 'usuario/list_researcher.html', context)

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
def index(request):
    pessoas = Pessoa.objects.all()
    historico = HistoricoReconhecimento.objects.all()[:10]
    return render(request, 'reconhecimento.html', {
        'pessoas': pessoas,
        'historico': historico
    })

@login_required
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
def dateil_researcher(request, id):

    user = Usuario.objects.get(id=id)
    return render(request, 'usuario/detail_researcher.html', {'user': user})

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
    
@login_required
def cadastrar_pessoa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            foto_data = data.get('foto_data')

            if not nome or not foto_data:
                return JsonResponse({'success': False, 'message': 'Dados incompletos'})

            if ';base64,' in foto_data:
                format, imgstr = foto_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = foto_data
                ext = 'jpg'

            foto = ContentFile(base64.b64decode(imgstr), name=f'{nome}.{ext}')
            
            pessoa = PessoaReconhecimento.objects.create(nome=nome, foto=foto)

            faces = DeepFace.extract_faces(img_path=pessoa.foto.path, detector_backend='opencv')
            if len(faces) == 0:
                pessoa.delete()
                return JsonResponse({'success': False, 'message': 'Nenhum rosto detectado na imagem'})

            

            embedding_obj = DeepFace.represent(
                img_path=pessoa.foto.path,
                model_name="ArcFace",
                enforce_detection=False
            )

            pessoa.embedding = embedding_obj[0]['embedding']
            pessoa.save()

            return JsonResponse({
                'success': True,
                'message': f'Pessoa {nome} cadastrada com sucesso!'
            })
        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'message': f'Erro: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def verificar_face(request):

    import numpy as np

    if request.method == 'POST':
        data = json.loads(request.body)
        foto_data = data.get('foto')
        
        if not foto_data:
            return JsonResponse({
                'success': False,
                'message': 'Nenhuma foto enviada'
            })
        
        format, imgstr = foto_data.split(';base64,')
        ext = format.split('/')[-1]
        foto = ContentFile(base64.b64decode(imgstr), name=f'verificacao.{ext}')
        
        historico = HistoricoReconhecimento.objects.create(
            foto_verificacao=foto
        )

        faces = DeepFace.extract_faces(
            img_path=historico.foto_verificacao.path,
            detector_backend='fastmtcnn',
            enforce_detection=False
        )
        if len(faces) == 0:
            return JsonResponse({'success': False, 'message': 'Nenhum rosto detectado na imagem'})
         
        try:

            melhor_match = None
            
            pessoas = PessoaReconhecimento.objects.exclude(embedding__isnull=True)
            
            backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'fastmtcnn',
                'retinaface', 'mediapipe', 'yolov8n', 'yolov8m', 'yolov8l', 'yolov11n',
                'yolov11s', 'yolov11m', 'yolov11l', 'yolov12n', 'yolov12s',
                'yolov12m', 'yolov12l', 'yunet', 'centerface'
            ]

            melhor_match = None
            melhor_confianca = 0
            melhor_distancia = float("inf")

            for pessoa in pessoas:
                verification = DeepFace.verify(
                    img1_path=historico.foto_verificacao.path,
                    img2_path=pessoa.foto.path,
                    detector_backend=backends[4],
                    model_name='ArcFace',
                    align=True,
                    enforce_detection=False
                )

                verified = verification.get('verified', False)
                distance = verification.get('distance', None)
                confidence = verification.get('confidence', None)

                if verified and distance is not None and distance < melhor_distancia:
                    melhor_match = pessoa
                    melhor_distancia = distance
                    melhor_confianca = confidence or (100 - distance * 100)

            if melhor_match:
                historico.pessoa = melhor_match
                historico.reconhecido = True
                historico.confianca = f'{melhor_confianca:.2f}'
                historico.save()

                result = []
                envs = EnvolvimentoCaso.objects.filter(pessoa=melhor_match.pessoa)

                for v in envs:
                    result.append({
                        'numero_caso': v.caso.numero_caso,
                        'tipo_crime': v.caso.tipo_crime.nome,
                        'data_envolvimento': v.data_envolvimento,
                        'titulo_caso': v.caso.titulo,
                        'estado_caso': v.caso.status,
                        'id_caso': v.caso.id,
                        'id_envolvimento': v.id,
                        'pessoa_id': melhor_match.pessoa.id
                    })

                return JsonResponse({
                    'success': True,
                    'reconhecido': True,
                    'pessoa': melhor_match.nome,
                    'image': melhor_match.foto.url,
                    'confianca': round(melhor_confianca, 2),
                    'message': f'Pessoa reconhecida: {melhor_match.nome}',
                    'envolvimento': result
                })
            else:
                historico.reconhecido = False
                historico.save()
                return JsonResponse({
                    'success': True,
                    'reconhecido': False,
                    'message': 'Pessoa não reconhecida no sistema'
                })
        except Exception as e:
            print(e)
            historico.delete()
            return JsonResponse({
                'success': False,
                'message': f'Erro ao processar: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

@login_required
def listar_pessoas(request):
    pessoas = Pessoa.objects.all().values('id', 'nome', 'foto', 'data_cadastro')
    return JsonResponse({'pessoas': list(pessoas)})


@login_required
def list_people(request):

    pessoas = Pessoa.objects.all()
    
    bi = request.GET.get('bi')
    nome = request.GET.get('nome')
    per_page = request.GET.get('per_page', 10)
    page = request.GET.get('page', 1)

    if nome:
        pessoas = pessoas.filter(nome_completo__icontains=nome)

    if bi:
        pessoas = pessoas.filter(bi__icontains=bi)

    paginator = Paginator(pessoas, per_page)

    obj = paginator.page(page)

    context={
        'pessoas': obj,
        'per_page': per_page,
    }
   
    return render(request, 'pessoa/list_people.html', context)

@login_required
def detail_people(request, id):

    pessoa = Pessoa.objects.get(id=id)

    return render(request, 'pessoa/detail_people.html', {'pessoa': pessoa})

@login_required
def edit_people(request, id):
    pessoa = Pessoa.objects.get(id=id)

    alias = None
    endereco = None

    try:

        alias = AliasPessoa.objects.get(pessoa=pessoa)

    except AliasPessoa.DoesNotExist:
        pass

    try:
        
        endereco = Endereco.objects.get(pessoa=pessoa)

    except Endereco.DoesNotExist:
        pass

    if request.method == 'POST':

        form = EditPessoaForm(request.POST)

        objetos = [obj for obj in [pessoa, endereco, alias] if obj is not None]

        dados_anteriores = serializers.serialize('json', objetos)

        if form.is_valid():

            pessoa, endereco, alias = form.save(pessoa=pessoa)
            endereco.save()

            objetos_novo = [obj for obj in [pessoa, endereco, alias] if obj is not None]

            LogAuditoria.objects.create(
                usuario=request.user,
                acao='update',
                modelo='Pessoa, Endereco, alias',
                objeto_id=str(pessoa.id),
                descricao=f'Pessoa, Endereço e alias Atualizados : {pessoa.nome_completo}',
                ip_origem=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                dados_anteriores = dados_anteriores,
                dados_novos = serializers.serialize('json', objetos_novo)
            )
            context={
                'pessoa': pessoa, 
                'form': form,
                'sucesso': 'Atualização feita com sucesso!',
                'endereco': endereco,
                'alias': alias
            }
            pessoa.data_nascimento = pessoa.data_nascimento.strftime('%Y-%m-%d')
            return render(request, 'pessoa/edit_people.html', context)
        else:
            context={
                'pessoa': pessoa, 
                'form': form,
                'erro': 'Erro ao Atualizar os dados!',
                'endereco': endereco,
                'alias': alias
            }
            pessoa.data_nascimento = pessoa.data_nascimento.strftime('%Y-%m-%d')
        
            return render(request, 'pessoa/edit_people.html', context)
        
    else:
        form = EditPessoaForm()
        context={
                'pessoa': pessoa, 
                'form': form,
                'endereco': endereco,
                'alias': alias
            }
        
        pessoa.data_nascimento = pessoa.data_nascimento.strftime('%Y-%m-%d')

        return render(request, 'pessoa/edit_people.html', context)
    
@login_required
@require_http_methods(["POST"])           
def delete_people(request, id):

    pessoa = Pessoa.objects.get(id=id)

    alias = None
    endereco = None

    try:

        alias = AliasPessoa.objects.get(pessoa=pessoa)

    except AliasPessoa.DoesNotExist:
        pass

    try:
        
        endereco = Endereco.objects.get(pessoa=pessoa)

    except Endereco.DoesNotExist:
        pass

    
    dados = json.dumps(request.body)

    password = dados.get('password')

    userLogin = request.user

    if not userLogin.check_password(password):
         return JsonResponse({'erro': 'Credinciais inválidas'}, status=403)

    pessoa.delete()

    if alias:
        alias.delete()

    if endereco:
        endereco.delete()

    LogAuditoria.objects.create(
        usuario=request.user,
        acao='delete',
        modelo='Usuaurio, Endereco, Alias',
        objeto_id=str(pessoa.id),
        descricao=f'Pessoa eliminada do sistema: {pessoa.nome_completo}',
        ip_origem=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return redirect('list_people')