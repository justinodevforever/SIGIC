from django.db import models
from usuario.models import Usuario
from casos.models import Caso
import uuid
import hashlib


class TipoEvidencia(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    requer_pericia = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nome

class Evidencia(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    STATUS_CHOICES = [
        ('coletada', 'Coletada'),
        ('em_analise', 'Em Análise'),
        ('analisada', 'Analisada'),
        ('devolvida', 'Devolvida'),
        ('destruida', 'Destruída'),
    ]
    
    numero_evidencia = models.CharField(max_length=50, unique=True)
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='evidencias')
    tipo = models.ForeignKey(TipoEvidencia, on_delete=models.PROTECT)
    descricao = models.TextField()
    
    data_coleta = models.DateTimeField()
    local_coleta = models.CharField(max_length=300)
    coletado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='evidencias_coletadas')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='coletada')
    custodia_atual = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='evidencias_custodia')
    local_armazenamento = models.CharField(max_length=200)
    
    peso = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    dimensoes = models.CharField(max_length=100, blank=True)
    cor = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    estado_conservacao = models.CharField(max_length=100, blank=True)
    
    observacoes = models.TextField(blank=True)
    valor_estimado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    lacrada = models.BooleanField(default=False)
    numero_lacre = models.CharField(max_length=50, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_coleta']
        indexes = [
            models.Index(fields=['numero_evidencia']),
            models.Index(fields=['caso']),
        ]
    
    def __str__(self):
        return f"{self.numero_evidencia} - {self.descricao[:50]}"

class Pericia(models.Model):

    id = models.UUIDField(
        primary_key = True,
        default=uuid.uuid4,
        editable=False
    )

    TIPOS = [
        ('DNA', 'DNA'),
        ('BALISTICA', 'Balística'),
        ('TOXICOLOGIA', 'Toxicologia'),
        ('DIGITAIS', 'Digitais')
    ]

    evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE, related_name='pericias')
    tipo = models.CharField(max_length=13, choices=TIPOS)
    resultado = models.TextField()
    conclusao = models.TextField()
    criado_por = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pericia_usuario')
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tipo}-{self.evidencia.numero_evidencia}'
    

class CadeiaCustomia(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    TIPO_MOVIMENTACAO_CHOICES = [
        ('coleta', 'Coleta'),
        ('transferencia', 'Transferência'),
        ('analise', 'Análise'),
        ('devolucao', 'Devolução'),
        ('armazenamento', 'Armazenamento'),
        ('destruicao', 'Destruição'),
    ]
    
    evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE, related_name='cadeia_custodia')
    tipo_movimentacao = models.CharField(max_length=20, choices=TIPO_MOVIMENTACAO_CHOICES)
    data_movimentacao = models.DateTimeField(auto_now_add=True)
    responsavel_anterior = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='transferencias_saida', null=True, blank=True)
    responsavel_atual = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='transferencias_entrada')
    local_origem = models.CharField(max_length=200, blank=True)
    local_destino = models.CharField(max_length=200)
    motivo = models.TextField()
    observacoes = models.TextField(blank=True)
    assinatura_digital = models.TextField(blank=True)  # Hash da transação

    def gerar_hash(self):

        dados = f'{self.tipo_movimentacao}{self.local_destino}{self.local_origem}{self.motivo}'

        return hashlib.sha256(dados.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):

        if not self.assinatura_digital:
            self.assinatura_digital = self.gerar_hash()
        
        super().save(*args, **kwargs)
    
    def verificar_autenticidade(self):

        if self.assinatura_digital == self.gerar_hash():

            return f'Movimentação íntegra e autenticada'
        
        else:
            return f'Movimentação Adulterada ou Corrompida'

    class Meta:
        ordering = ['-data_movimentacao']
    
    def __str__(self):
        return f"{self.evidencia.numero_evidencia} - {self.tipo_movimentacao} - {self.data_movimentacao}"

def upload_arquivo_path(instance, filename):
    print(instance)
    
    return f"casos/{instance.evidencia.numero_evidencia}/arquivos/{filename}"

class Arquivo(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    TIPO_ARQUIVO_CHOICES = [
        ('documento', 'Documento'),
        ('foto', 'Fotografia'),
        ('video', 'Vídeo'),
        ('audio', 'Áudio'),
        ('relatorio', 'Relatório'),
        ('laudo', 'Laudo'),
        ('outro', 'Outro'),
    ]
    
    evidencia = models.ForeignKey(Evidencia, on_delete=models.CASCADE, related_name='arquivos', null=True, blank=True)
    nome_arquivo = models.CharField(max_length=255)
    tipo_arquivo = models.CharField(max_length=20, choices=TIPO_ARQUIVO_CHOICES)
    arquivo = models.FileField(upload_to='evidence/')
    tamanho_arquivo = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    data_upload = models.DateTimeField(auto_now_add=True)
    uploadado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    resolucao = models.CharField(max_length=20, blank=True)
    duracao = models.IntegerField(null=True, blank=True)  # em segundos
    confidencial = models.BooleanField(default=False)
    hash_arquivo = models.CharField(max_length=64, blank=True)
    
    def gerar_hash(self):
        sha256 = hashlib.sha256()
        if self.arquivo and hasattr(self.arquivo, 'open'):
            
            self.arquivo.open('rb')
            for chunk in iter(lambda: self.arquivo.read(8192), b''):
                sha256.update(chunk)
            
            self.arquivo.seek(0) 
        sha256.update(self.tipo_arquivo.encode('utf-8'))
        return sha256.hexdigest()

    def save(self, *args, **kwargs):

        if not self.hash_arquivo:
            self.hash_arquivo = self.gerar_hash()
            
        
        super().save(*args, **kwargs)
        
    def verificar_autenticidade(self):

        if self.hash_arquivo == self.gerar_hash():

            return f'Assinatura íntegra e autenticada'
        
        else:
            return f'Assinatura Adulterada ou Corrompida'
    
    class Meta:
        ordering = ['-data_upload']
    
    def __str__(self):
        return f"{self.nome_arquivo} - {self.evidencia.numero_evidencia}"