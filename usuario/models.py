from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid
from datetime import date

class Pessoa(models.Model):
    
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
    
    nome_completo = models.CharField(max_length=200)
    nome_social = models.CharField(max_length=200, blank=True)
    bi = models.CharField(max_length=14, null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True)
    
    altura = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cor_olhos = models.CharField(max_length=20, blank=True)
    cor_cabelo = models.CharField(max_length=20, blank=True)
    
    profissao = models.CharField(max_length=100, blank=True)
    escolaridade = models.CharField(max_length=50, blank=True)
    nacionalidade = models.CharField(max_length=50, default='Angolana')
    
    telefone_principal = models.CharField(max_length=20, blank=True)
    telefone_secundario = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    


    @property
    def idade(self):
        hoje = date.today()

        return hoje.year - self.data_nascimento.year -(
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
    
    class Meta:
        ordering = ['nome_completo']
        indexes = [
            models.Index(fields=['nome_completo']),
            models.Index(fields=['bi']),
        ]
    

    def __str__(self):
        return self.nome_completo


class Usuario(AbstractUser):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    CARGO_CHOICES = [
        ('delegado', 'Delegado'),
        ('investigador', 'Investigador'),
        ('escrivao', 'Escrivão'),
        ('perito', 'Perito'),
        ('analista', 'Analista'),
        ('chefe', 'Chefe de Departamento'),
        ('admin', 'Administrador'),
    ]
    
    NIVEL_ACESSO_CHOICES = [
        (1, 'Básico'),
        (2, 'Intermediário'),
        (3, 'Avançado'),
        (4, 'Total'),
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
    
    data_nascimento = models.DateField(null=True, blank=True)
    matricula = models.CharField(max_length=20, unique=True)
    cargo = models.CharField(max_length=20, choices=CARGO_CHOICES)
    departamento = models.CharField(max_length=100)
    nivel_acesso = models.IntegerField(choices=NIVEL_ACESSO_CHOICES, default=1)
    telefone = models.CharField(max_length=20, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES,null=True, blank=True)
    bi = models.CharField(max_length=14, null=True, blank=True)
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES, blank=True)
    ultimo_login_ip = models.GenericIPAddressField(null=True, blank=True)

    @property
    def idade(self):
        hoje = date.today()

        return hoje.year - self.data_nascimento.year -(
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )

    def __str__(self):
        return f"{self.get_full_name()} - {self.cargo} {self.username}"

class profile(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )


    image = models.FileField(upload_to='profile')
    data_criacao = models.DateField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return self.image


class PerfilAcesso(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    pode_criar_casos = models.BooleanField(default=False)
    pode_editar_casos = models.BooleanField(default=False)
    pode_deletar_casos = models.BooleanField(default=False)
    pode_ver_casos_outros = models.BooleanField(default=False)
    pode_gerenciar_evidencias = models.BooleanField(default=False)
    pode_gerar_relatorios = models.BooleanField(default=False)
    pode_administrar_sistema = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nome


class RegistroReconhecimento(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, null=True, blank=True)
    imagem_capturada = models.ImageField(upload_to='reconhecimentos/')
    data_hora = models.DateTimeField(auto_now_add=True)
    confianca = models.FloatField(null=True, blank=True)
    reconhecida = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-data_hora']
    
    def __str__(self):
        if self.pessoa:
            return f"{self.pessoa.nome} - {self.data_hora}"
        return f"Desconhecido - {self.data_hora}"

class Conexao(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    TIPOS = [
        ('financeira', 'Financeira'),
        ('familiar', 'Financeira'),
        ('criminal', 'Criminal'),
        ('amizade', 'Amizade'),
    ]
    GRAU_CONFIANCA = [
        ('confirmado', 'Confirmado'),
        ('suspeito', 'Suspeito'),
    ]

    pessoa_origem = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='conexao_origem')
    pessoa_destino = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='conexao_destino')
    tipo = models.CharField(max_length=20)
    grau_confianca = models.CharField(max_length=50)
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='conexao_usuario')

    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pessoa_origem} ---> {self.pessoa_destino} -- {self.tipo}'
    


class AliasPessoa(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='aliases')
    nome_alias = models.CharField(max_length=200)
    tipo_alias = models.CharField(max_length=50, choices=[
        ('apelido', 'Apelido'),
        ('nome_guerra', 'Nome de Guerra'),
        ('nome_falso', 'Nome Falso'),
        ('outro', 'Outro'),
    ])
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.pessoa.nome_completo} - {self.nome_alias}"

class Endereco(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    TIPO_ENDERECO_CHOICES = [
        ('residencial', 'Residencial'),
        ('comercial', 'Comercial'),
        ('temporario', 'Temporário'),
        ('antigo', 'Antigo'),
    ]
    
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='enderecos')
    tipo = models.CharField(max_length=20, choices=TIPO_ENDERECO_CHOICES, blank=True)
    logradouro = models.CharField(max_length=200, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2,  blank=True)
    ponto_referencia = models.CharField(max_length=200, blank=True)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.cidade}/{self.estado}"



class LogAuditoria(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    TIPO_ACAO_CHOICES = [
        ('create', 'Criação'),
        ('update', 'Atualização'),
        ('delete', 'Exclusão'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access', 'Acesso'),
        ('export', 'Exportação'),
        ('print', 'Impressão'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=20, choices=TIPO_ACAO_CHOICES)
    modelo = models.CharField(max_length=100)  
    objeto_id = models.CharField(max_length=100) 
    descricao = models.TextField()
    ip_origem = models.GenericIPAddressField()
    user_agent = models.TextField()
    data_acao = models.DateTimeField(auto_now_add=True)
    
    dados_anteriores = models.JSONField(null=True, blank=True)
    dados_novos = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-data_acao']
        indexes = [
            models.Index(fields=['usuario', 'data_acao']),
            models.Index(fields=['modelo', 'objeto_id']),
        ]
    
    def __str__(self):
        return f"{self.usuario} - {self.acao} - {self.modelo} - {self.data_acao}"

class ConfiguracaoSistema(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    chave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    descricao = models.TextField()
    tipo_valor = models.CharField(max_length=20, choices=[
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ])
    editavel = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.chave} = {self.valor}"
        
from django.core.files.storage import FileSystemStorage
import os

class PessoaReconhecimento(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    nome = models.CharField(max_length=400)
    foto = models.ImageField(upload_to='faces/')
    embedding = models.JSONField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='envolvimento')
    
    def __str__(self):
        return f'{self.pessoa.nome_completo}-{self.nome}'
    
    class Meta:
        ordering = ['-data_cadastro']
        verbose_name_plural = "Reconhecimentos"
        indexes = [
            models.Index(fields=['nome']),
            models.Index(fields=['foto']),
            models.Index(fields=['embedding']),
        ]

class HistoricoReconhecimento(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    pessoa = models.ForeignKey(PessoaReconhecimento, on_delete=models.CASCADE, null=True, blank=True)
    foto_verificacao = models.ImageField(upload_to='verificacoes/')
    confianca = models.FloatField(null=True, blank=True)
    reconhecido = models.BooleanField(default=False)
    data_verificacao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.foto_verificacao.path
    class Meta:
        verbose_name_plural = "Histórico de Reconhecimentos"
        ordering = ['-data_verificacao']
        