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



from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import PessoaReconhecimento, HistoricoReconhecimento
from deepface import DeepFace
import base64
import json
import numpy as np


def index(request):
    pessoas = Pessoa.objects.all()
    historico = HistoricoReconhecimento.objects.all()[:10]
    return render(request, 'reconhecimento.html', {
        'pessoas': pessoas,
        'historico': historico
    })

def cadastrar_pessoa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nome = data.get('nome')
            foto_data = data.get('foto_data')

            if not nome or not foto_data:
                return JsonResponse({'success': False, 'message': 'Dados incompletos'})

            # Verificar formato base64
            if ';base64,' in foto_data:
                format, imgstr = foto_data.split(';base64,')
                ext = format.split('/')[-1]
            else:
                imgstr = foto_data
                ext = 'jpg'


            # Decodificar imagem
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
            detector_backend='opencv',
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
            for pessoa in pessoas:

                verification = DeepFace.verify(
                    img1_path=historico.foto_verificacao.path,
                    img2_path=pessoa.foto.path,
                    detector_backend=backends[3],
                    model_name='ArcFace',
                    distance_metric="cosine",
                    align=True,
                )    
                melhor_match = pessoa
            
            if verification['verified']:
                confianca = verification['confidence']
                historico.pessoa = melhor_match
                historico.reconhecido = True
                historico.confianca = f'{confianca:.2f}'
                historico.save()
                
                return JsonResponse({
                    'success': True,
                    'reconhecido': True,
                    'pessoa': melhor_match.nome,
                    'image': melhor_match.foto.url,
                    'confianca': round(confianca, 2),
                    'message': f'Pessoa reconhecida: {melhor_match.nome}'
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

def listar_pessoas(request):
    pessoas = Pessoa.objects.all().values('id', 'nome', 'foto', 'data_cadastro')
    return JsonResponse({'pessoas': list(pessoas)})

def deletar_pessoa(request, pessoa_id):
    if request.method == 'DELETE':
        try:
            pessoa = Pessoa.objects.get(id=pessoa_id)
            pessoa.delete()
            return JsonResponse({'success': True, 'message': 'Pessoa deletada'})
        except Pessoa.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Pessoa não encontrada'})
    return JsonResponse({'success': False, 'message': 'Método não permitido'})

    