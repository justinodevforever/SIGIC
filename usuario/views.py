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



from django.http import JsonResponse
from django.core.files.base import ContentFile
from .models import PessoaReconhecimento, HistoricoReconhecimento
from deepface import DeepFace
import base64
import json
import numpy as np
from casos.models import Caso, EnvolvimentoCaso


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
                    detector_backend=backends[4],  # fastmtcnn
                    model_name='ArcFace',
                    align=True,
                    enforce_detection=False
                )

                verified = verification.get('verified', False)
                distance = verification.get('distance', None)
                confidence = verification.get('confidence', None)

                # Para ArcFace: menor distância = melhor match
                if verified and distance is not None and distance < melhor_distancia:
                    melhor_match = pessoa
                    melhor_distancia = distance
                    melhor_confianca = confidence or (100 - distance * 100)

            # 🧠 Depois do loop, decide se reconheceu ou não
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
    

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os

class TratamentoImagemFacial:
    
    def __init__(self, tamanho_minimo=300, tamanho_maximo=1920):
        self.tamanho_minimo = tamanho_minimo
        self.tamanho_maximo = tamanho_maximo
    
    def carregar_imagem(self, caminho):
    
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Imagem não encontrada: {caminho}")
        
        img = cv2.imread(caminho)
        if img is None:
            raise ValueError(f"Não foi possível ler a imagem: {caminho}")
        
        return img
    
    def redimensionar_inteligente(self, img):
        
        height, width = img.shape[:2]
        
        # Se muito pequena, aumentar
        if width < self.tamanho_minimo or height < self.tamanho_minimo:
            scale = max(self.tamanho_minimo / width, self.tamanho_minimo / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Se muito grande, reduzir
        elif width > self.tamanho_maximo or height > self.tamanho_maximo:
            scale = min(self.tamanho_maximo / width, self.tamanho_maximo / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
    
    def corrigir_iluminacao(self, img):
        """Corrige problemas de iluminação"""
        # Converter para LAB
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Juntar canais
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return img
    
    def ajustar_brilho_contraste(self, img, brilho=0, contraste=0):
       
        if brilho != 0:
            if brilho > 0:
                shadow = brilho
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brilho
            alpha_b = (highlight - shadow) / 255
            gamma_b = shadow
            img = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)
        
        if contraste != 0:
            f = 131 * (contraste + 127) / (127 * (131 - contraste))
            alpha_c = f
            gamma_c = 127 * (1 - f)
            img = cv2.addWeighted(img, alpha_c, img, 0, gamma_c)
        
        return img
    
    def remover_ruido(self, img):
      
        # Bilateral filter preserva bordas
        img = cv2.bilateralFilter(img, 9, 75, 75)
        return img
    
    def aumentar_nitidez(self, img, intensidade=1.5):
        
        # Kernel de nitidez
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) * intensidade / 9
        
        img = cv2.filter2D(img, -1, kernel)
        return img
    
    def corrigir_cores(self, img):
      
        # Converter para PIL para ajustes mais suaves
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        
        # Ajustar saturação levemente
        enhancer = ImageEnhance.Color(img_pil)
        img_pil = enhancer.enhance(1.1)
        
        # Converter de volta para OpenCV
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        return img
    
    def detectar_e_rotacionar(self, img):
       
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                
                # Se detectar 2 olhos, calcular ângulo
                if len(eyes) >= 2:
                    
                    eye1 = eyes[0]
                    eye2 = eyes[1]
                    
                    # Centros dos olhos
                    eye1_center = (x + eye1[0] + eye1[2]//2, y + eye1[1] + eye1[3]//2)
                    eye2_center = (x + eye2[0] + eye2[2]//2, y + eye2[1] + eye2[3]//2)
                    
                  
                    dx = eye2_center[0] - eye1_center[0]
                    dy = eye2_center[1] - eye1_center[1]
                    angle = np.degrees(np.arctan2(dy, dx))
                    
                   
                    if abs(angle) > 2:
                        center = tuple(np.array(img.shape[1::-1]) / 2)
                        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
                        img = cv2.warpAffine(img, rot_mat, img.shape[1::-1], 
                                           flags=cv2.INTER_LINEAR)
        
        return img
    
    def normalizar_exposicao(self, img):
       
        # Converter para YCrCb
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        channels = cv2.split(ycrcb)
        
        # Equalizar apenas o canal Y (luminância)
        channels[0] = cv2.equalizeHist(channels[0])
        
   
        ycrcb = cv2.merge(channels)
        img = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        
        return img
    
    def processar_completo(self, caminho_entrada, caminho_saida=None, 
                          salvar=True, mostrar_original=False):
        """
        Pipeline completo de processamento
        """
        print(f"Processando: {caminho_entrada}")
    
        img_original = self.carregar_imagem(caminho_entrada)
        img = img_original.copy()
        
        print(f"  Tamanho original: {img.shape[1]}x{img.shape[0]}")
        
      
        img = self.redimensionar_inteligente(img)
        print(f"  Tamanho ajustado: {img.shape[1]}x{img.shape[0]}")
        
      
        img = self.detectar_e_rotacionar(img)
        print("  Rotação corrigida")
        
        
        img = self.remover_ruido(img)
        print("  Ruído removido")
        
       
        img = self.corrigir_iluminacao(img)
        print("  Iluminação corrigida")
        
   
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brilho_medio = np.mean(gray)
        
        if brilho_medio < 100:
            ajuste_brilho = int((100 - brilho_medio) / 2)
            img = self.ajustar_brilho_contraste(img, brilho=ajuste_brilho, contraste=10)
            print(f"  Brilho ajustado (+{ajuste_brilho})")
        elif brilho_medio > 155:
            ajuste_brilho = -int((brilho_medio - 155) / 2)
            img = self.ajustar_brilho_contraste(img, brilho=ajuste_brilho, contraste=10)
            print(f"  Brilho ajustado ({ajuste_brilho})")
        
        
        img = self.normalizar_exposicao(img)
        print("  Exposição normalizada")
        
    
        img = self.corrigir_cores(img)
        print("  Cores corrigidas")
        
     
        img = self.aumentar_nitidez(img, intensidade=1.3)
        print("  Nitidez aumentada")
        
      
        if salvar:
            if caminho_saida is None:
                nome, ext = os.path.splitext(caminho_entrada)
                caminho_saida = f"{nome}_processado{ext}"
            
            cv2.imwrite(caminho_saida, img)
            print(f"✓ Salvo em: {caminho_saida}")
        
        # Mostrar comparação
        if mostrar_original:
            img_comparacao = np.hstack([
                cv2.resize(img_original, (400, 400)),
                cv2.resize(img, (400, 400))
            ])
            cv2.imshow('Original vs Processado', img_comparacao)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        return img, caminho_saida if salvar else None


if __name__ == "__main__":
  
    processador = TratamentoImagemFacial(tamanho_minimo=300, tamanho_maximo=1920)

    try:
        img_processada, caminho_saida = processador.processar_completo(
            caminho_entrada="sua_foto.jpg",
            caminho_saida="foto_processada.jpg",
            mostrar_original=False
        )
        print("\n✓ Processamento concluído com sucesso!")
        
    except Exception as e:
        print(f"\n✗ Erro: {e}")
    
