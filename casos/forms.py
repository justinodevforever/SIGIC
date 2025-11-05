from django import forms
from usuario.models import Usuario
from django.core.exceptions import ValidationError
from datetime import datetime, date
from .models import *
from usuario.models import *
from django.utils import timezone
from evidencias.models import Evidencia
from decimal import Decimal
import re
from django.http import JsonResponse
from django.core.files.base import ContentFile
from deepface import DeepFace
import base64
import json
import numpy as np
import tempfile
import os

class PessoaEnvolvidaForm(forms.Form):

    TIPO_ENVOLVIMENTO_CHOICES = [
        ('suspeito', 'Suspeito'),
        ('vitima', 'Vítima'),
        ('testemunha', 'Testemunha'),
        ('informante', 'Informante'),
        ('outro', 'Outro'),
    ]
    
    TIPO_PESSOA_CHOICES = [
        ('suspeito', 'Suspeito'),
        ('vitima', 'Vítima'),
        ('testemunha', 'Testemunha'),
        ('informante', 'Informante'),
        ('outro', 'Outro'),
    ]
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
        ('N', 'Não informado'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('solteiro', 'Solteiro(a)'),
        ('casado', 'Casado(a)'),
        ('divorciado', 'Divorciado(a)'),
        ('viuvo', 'Viúvo(a)'),
        ('uniao_estavel', 'União Estável'),
    ]

    nome_completo = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    nome_social = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    altura = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control', 'step': '0.01'}
    ))
    peso = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control', 'step': '0.01'}
    ))
    cor_olhos = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    cor_cabelo = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))

    bi = forms.CharField(
        required=True,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    profissao = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    escolaridade = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    nacionalidade = forms.CharField(
        required=True,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    telefone_principal = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    telefone_secundario = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    email = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))

    data_nascimento = forms.DateField(
        required=True,
        widget= forms.DateInput( attrs={'class': 'form-control'}
    ))
    genero = forms.ChoiceField(
        choices= GENERO_CHOICES,
        required=True,
        widget= forms.Select(attrs={'class': 'form-control'}
    ))
    estado_civil = forms.ChoiceField(
        choices =  ESTADO_CIVIL_CHOICES,
        required=True,
        widget= forms.Select( attrs={
            'class': 'form-control',
            }
    ))
    tipo_envolvimento = forms.ChoiceField(
        choices = TIPO_ENVOLVIMENTO_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    observacoes = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    descricao = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))

    tipo_alias = forms.ChoiceField(
        choices=[
            ('apelido', 'Apelido'),
            ('nome_guerra', 'Nome de Guerra'),
            ('nome_falso', 'Nome Falso'),
            ('outro', 'Outro'),
        ],
        required=False,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    nome_alias = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))

    tipo_endereco = forms.ChoiceField(
        choices=[
            ('residencial', 'Residencial'),
            ('comercial', 'Comercial'),
            ('temporario', 'Temporário'),
            ('antigo', 'Antigo'),
        ],
        required=False,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    logradouro = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    numero = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    complemento = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    bairro = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    cidade = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    estado = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    ponto_referencia = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))

    def clean(self):

        cleaned_data = super().clean()

        telefone_principal = cleaned_data.get('telefone_principal')
        telefone_secundario = cleaned_data.get('telefone_secundario')
        telefone_principal = telefone_principal.replace(" ","")
        telefone_secundario = telefone_secundario.replace(" ","")

        if telefone_principal and not re.fullmatch(r'9\d{8}', telefone_principal):

            self.add_error('telefone_principal', 'Número de telefone inválido')

        if telefone_secundario and not re.fullmatch(r'9\d{8}', telefone_secundario):

            self.add_error('telefone_secundario', 'Número de telefone inválido')

        return cleaned_data

    def save(self,caso=None, envolvimento=None):
        

        if envolvimento is None:

            telefone_principal=self.cleaned_data['telefone_principal']
            telefone_secundario=self.cleaned_data['telefone_secundario']
            telefone_principal = telefone_principal.replace(" ","")
            telefone_secundario = telefone_secundario.replace(" ","")
            
            altura = self.cleaned_data['altura']
            peso = self.cleaned_data['peso']

            if altura in (None, ""):

                altura = None
            elif isinstance(altura, str):
                altura = altura.replace(',','.')
                altura = Decimal(altura)

            if peso in (None, ""):

                peso = None
            elif isinstance(peso, str):
                peso = peso.replace(',','.')
                peso = Decimal(peso)

            pessoa = Pessoa(

                nome_completo=self.cleaned_data['nome_completo'],
                nome_social=self.cleaned_data['nome_social'],
                bi=self.cleaned_data['bi'],
                data_nascimento=self.cleaned_data['data_nascimento'],
                genero=self.cleaned_data['genero'],
                estado_civil=self.cleaned_data['estado_civil'],
                cor_olhos=self.cleaned_data['cor_olhos'],
                altura=altura,
                peso=peso,
                cor_cabelo=self.cleaned_data['cor_cabelo'],
                profissao=self.cleaned_data['profissao'],
                escolaridade=self.cleaned_data['escolaridade'],
                nacionalidade=self.cleaned_data['nacionalidade'],
                telefone_principal=telefone_principal,
                telefone_secundario=telefone_secundario,
                email=self.cleaned_data['email'],
                observacoes=self.cleaned_data['observacoes'],
            )

            pessoa.save()

            

            envolvimentoCaso = EnvolvimentoCaso(
                descricao=self.cleaned_data['descricao'],
                caso=caso,
                pessoa=pessoa,
                tipo_envolvimento=self.cleaned_data['tipo_envolvimento'],
            )

            envolvimentoCaso.save()

            if self.cleaned_data['tipo_endereco']:
                endereco = Endereco(
                    pessoa=pessoa,
                    tipo=self.cleaned_data['tipo_endereco'],
                    logradouro=self.cleaned_data['logradouro'],
                    numero=self.cleaned_data['numero'],
                    complemento=self.cleaned_data['complemento'],
                    bairro=self.cleaned_data['bairro'],
                    ponto_referencia=self.cleaned_data['ponto_referencia'],
                    cidade=self.cleaned_data['cidade'],
                    estado=self.cleaned_data['estado'],
                )

                endereco.save()

            if self.cleaned_data['tipo_alias']:

                alias = AliasPessoa(
                    pessoa=pessoa,
                    tipo_alias=self.cleaned_data['tipo_alias'],
                    nome_alias=self.cleaned_data['nome_alias'],
                )

                alias.save()

            return pessoa, envolvimentoCaso
            
        else:        

            print(envolvimento.id)
            envolvimento.tipo_envolvimento=self.cleaned_data['tipo_envolvimento'],
            envolvimento.observacoes=self.cleaned_data['observacoes'],
            

            envolvimento.save()

            return envolvimento
        
class FormEnvolvimento(forms.Form):

    tipo_envolvimento = forms.ChoiceField(
        choices = EnvolvimentoCaso.TIPO_ENVOLVIMENTO_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))

    descricao = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))


    def save(self, envolvimento):

        envolvimento.tipo_envolvimento=self.cleaned_data['tipo_envolvimento']
        envolvimento.descricao=self.cleaned_data['descricao']
        

        envolvimento.save()

        return envolvimento

class CasoForm(forms.Form):
    
    
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('suspenso', 'Suspenso'),
        ('concluido', 'Concluído'),
        ('arquivado', 'Arquivado'),
    ]
    
    PRIORIDADE_CHOICES = [
        (1, 'Baixa'),
        (2, 'Normal'),
        (3, 'Alta'),
        (4, 'Urgente'),
        (5, 'Crítica'),
    ]

    choices_gravidade=[
        (1, 'Leve'),
        (2, 'Média'),
        (3, 'Grave'),
        (4, 'Gravíssima'),
    ]

    delegacia_origem = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    titulo = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    observacoes_internas = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))

    prazo_conclusao = forms.DateTimeField(
        required=False,
        widget= forms.DateInput( attrs={'class': 'form-control'}
    ))
    data_conclusao = forms.DateTimeField(
        required=False,
        widget= forms.DateInput( attrs={'class': 'form-control'}
    ))
    data_ocorrencia = forms.DateTimeField(
        required=False,
        widget= forms.DateTimeInput( attrs={'class': 'form-control'}
    ))
    local_ocorrencia = forms.CharField(
        required=True,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    delegacia_origem = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    investigador_principal = forms.ModelChoiceField(
        queryset= Usuario.objects.filter(
        cargo='investigador'),
        error_messages={
            'required': 'Por favor, selecione um Investigador.',
            'invalid_choice': 'O usuário selecionado não é válido, ele não é um Investigador!'
        },
        required=True,
        widget= forms.Select(attrs={'class': 'form-control'}
    ))
    investigadores_apoio = forms.ModelMultipleChoiceField(
        queryset=  Usuario.objects.filter(
        cargo='investigador'),
        error_messages={
            'required': 'Por favor, selecione um Investigador.',
            'invalid_choice': 'O usuário selecionado não é válido, ele não é um Investigador!'
        },
        required=False,
        widget= forms.SelectMultiple( attrs={
            'class': 'form-control',
            }
    ))
    delegado_responsavel = forms.ModelChoiceField(
        queryset= Usuario.objects.filter(
        cargo='delegado'),
        required=True,
        error_messages={
            'required': 'Por favor, selecione um delegado responsável.',
            'invalid_choice': 'O usuário selecionado não é válido, ele não é um delegado!'
        },
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    prioridade = forms.ChoiceField(
        choices=PRIORIDADE_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    observacoes = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))

    tipo_crime = forms.ModelChoiceField(
        queryset= TipoCrime.objects.filter(ativo=True),
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    

    def __init__(self, *args, **kwargs):

        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    
    def clean(self):
        cleaned_data = super().clean()


        return cleaned_data

    def save(self, caso=None):

        if caso is None:

            ano_atual = timezone.now().year

            numero = 0

            ultimo_caso = Caso.objects.filter(
                numero_caso__startswith=str(ano_atual)
            ).order_by('data_abertura').last()

            if ultimo_caso:
                numero = int(ultimo_caso.numero_caso.split('-')[1]) + 1

            else:
                numero = 1

            numero_caso = f'{ano_atual}-{numero}'

            caso = Caso(
                tipo_crime=self.cleaned_data['tipo_crime'],
                numero_caso=numero_caso,
                titulo=self.cleaned_data['titulo'],
                prazo_conclusao=self.cleaned_data['prazo_conclusao'],
                data_conclusao=self.cleaned_data['data_conclusao'],
                data_ocorrencia=self.cleaned_data['data_ocorrencia'],
                delegacia_origem=self.cleaned_data['delegacia_origem'],
                delegado_responsavel=self.cleaned_data['delegado_responsavel'],
                investigador_principal=self.cleaned_data['investigador_principal'],
                observacoes_internas=self.cleaned_data['observacoes_internas'],
                observacoes=self.cleaned_data['observacoes'],
                prioridade=self.cleaned_data['prioridade'],
                local_ocorrencia=self.cleaned_data['local_ocorrencia'],
                status=self.cleaned_data['status'],
                comarca='meu'
            )

            caso.save()

            caso.investigadores_apoio.set(self.cleaned_data['investigadores_apoio'])
        else:
            self.instance.titulo=self.cleaned_data['titulo']
            self.instance.prazo_conclusao=self.cleaned_data['prazo_conclusao']
            self.instance.data_conclusao=self.cleaned_data['data_conclusao']
            self.instance.data_ocorrencia=self.cleaned_data['data_ocorrencia']
            self.instance.delegacia_origem=self.cleaned_data['delegacia_origem']
            self.instance.delegado_responsavel=self.cleaned_data['delegado_responsavel']
            self.instance.investigador_principal=self.cleaned_data['investigador_principal']
            self.instance.observacoes_internas=self.cleaned_data['observacoes_internas']
            self.instance.observacoes=self.cleaned_data['observacoes']
            self.instance.prioridade=self.cleaned_data['prioridade']
            self.instance.local_ocorrencia=self.cleaned_data['local_ocorrencia']
            self.instance.status=self.cleaned_data['status']
            
            self.instance.save()

        return caso

class EventoTimelineForm(forms.Form):

    TIPO_EVENTO_CHOICES = [
        ('crime', 'Ocorrência do Crime'),
        ('denuncia', 'Denúncia/Descoberta'),
        ('prisao', 'Prisão'),
        ('depoimento', 'Depoimento'),
        ('pericia', 'Perícia'),
        ('busca_apreensao', 'Busca e Apreensão'),
        ('audiencia', 'Audiência'),
        ('sentenca', 'Sentença'),
        ('recurso', 'Recurso'),
        ('outro', 'Outro'),
    ]
    
    IMPORTANCIA_CHOICES = [
        (1, 'Baixa'),
        (2, 'Média'),
        (3, 'Alta'),
        (4, 'Crítica'),
    ]
    
    localizacao = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'},
    ))
    titulo = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    descricao = forms.CharField(
        required=True,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    observacoes = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    coordenadas_lat = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control', 'id':"la",
        "step":"0.00000001"},
    ))
    coordenadas_lng = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control', 'id':"lo",
        "step":"0.00000001"},
    ))


    data_hora = forms.DateTimeField(
        required=True,
        widget= forms.DateInput( attrs={'class': 'form-control'}
    ))

    investigador_principal = forms.ModelChoiceField(
        queryset= Usuario.objects.filter(
        cargo='investigador'),
        required=True,
        widget= forms.Select(attrs={'class': 'form-control'}
    ))
    pessoas_envolvidas = forms.ModelMultipleChoiceField(
        queryset=  Pessoa.objects.none(),
        required=False,
        widget= forms.SelectMultiple( attrs={
            'class': 'form-control',
            }
    ))
    evidencias_relacionadas = forms.ModelMultipleChoiceField(
        queryset=  Evidencia.objects.none(),
        required=False,
        widget= forms.SelectMultiple( attrs={
            'class': 'form-control',
            }
    ))

    tipo_evento = forms.ChoiceField(
        choices=TIPO_EVENTO_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    importancia = forms.ChoiceField(
        choices=IMPORTANCIA_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))  
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        pessoas = Pessoa.objects.filter(envolvimentos__caso=self.instance)

        self.fields['pessoas_envolvidas'].queryset = pessoas
        self.fields['evidencias_relacionadas'].queryset = Evidencia.objects.filter(caso=self.instance)
        
    def save(self, evento=None):
        coordenadas_lat = self.cleaned_data['coordenadas_lat']
        coordenadas_lng = self.cleaned_data['coordenadas_lng']


        if coordenadas_lat:
            coordenadas_lat = coordenadas_lat.replace(',','.')
            
        if coordenadas_lng:
            coordenadas_lng = coordenadas_lng.replace(',','.')

        if evento is None:
            even = EventoTimeline(
                caso=self.instance,
                titulo=self.cleaned_data['titulo'],
                localizacao=self.cleaned_data['localizacao'],
                descricao=self.cleaned_data['descricao'],
                coordenadas_lat=coordenadas_lat,
                coordenadas_lng=coordenadas_lng,
                data_hora=self.cleaned_data['data_hora'],
                investigador_responsavel=self.cleaned_data['investigador_principal'],
                tipo_evento=self.cleaned_data['tipo_evento'],
                importancia=self.cleaned_data['importancia'],
                observacoes=self.cleaned_data['observacoes'],
            )

            even.save()

            even.pessoas_envolvidas.set(self.cleaned_data['pessoas_envolvidas'])
            even.evidencias_relacionadas.set(self.cleaned_data['evidencias_relacionadas'])
            return even

        else:
            evento.titulo=self.cleaned_data['titulo']
            evento.localizacao=self.cleaned_data['localizacao']
            evento.descricao=self.cleaned_data['descricao']
            evento.coordenadas_lat=self.cleaned_data['coordenadas_lat']
            evento.coordenadas_lng=self.cleaned_data['coordenadas_lng']
            evento.data_hora=self.cleaned_data['data_hora']
            evento.investigador_responsavel=self.cleaned_data['investigador_principal']
            evento.tipo_evento=self.cleaned_data['tipo_evento']
            evento.importancia=self.cleaned_data['importancia']
            evento.observacoes=self.cleaned_data['observacoes']

            evento.save()

            evento.pessoas_envolvidas.set(self.cleaned_data['pessoas_envolvidas'])
            evento.evidencias_relacionadas.set(self.cleaned_data['evidencias_relacionadas'])

            return evento
    
class TipoCrimeForm(forms.Form):

    nome = forms.CharField(
        required=True,
        widget= forms.TextInput(attrs={'class': 'form-control'})
    )

    gravidade = forms.ChoiceField(
        choices=[
            (1, 'Leve'),
            (2, 'Média'),
            (3, 'Grave'),
            (4, 'Gravíssima'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    descricao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'form': 'form-control'})
    )
    ativo = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'form': 'form-control'})
    )


    def save(self, tipo_crime=None):

        if not tipo_crime:

            tipo = TipoCrime(
                nome=self.cleaned_data['nome'],
                gravidade=self.cleaned_data['gravidade'],
                descricao=self.cleaned_data['descricao'],
            )

            tipo.save()

            return tipo
        
        else:

            tipo_crime.nome = self.cleaned_data['nome']
            tipo_crime.gravidade = self.cleaned_data['gravidade']
            tipo_crime.descricao = self.cleaned_data['descricao']
            tipo_crime.ativo = self.cleaned_data['ativo']

            tipo_crime.save()

            return tipo_crime