from django.db import models
from usuario.models import Pessoa, Usuario
import uuid



class TipoCrime(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    gravidade = models.IntegerField(choices=[
        (1, 'Leve'),
        (2, 'Média'),
        (3, 'Grave'),
        (4, 'Gravíssima'),
    ])
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f" {self.nome}"

class Caso(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
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
    
    numero_caso = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo_crime = models.ForeignKey(TipoCrime, on_delete=models.PROTECT)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    prioridade = models.IntegerField(choices=PRIORIDADE_CHOICES, default=2)
    
    data_ocorrencia = models.DateTimeField()
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    prazo_conclusao = models.DateTimeField(null=True, blank=True)
    
    local_ocorrencia = models.CharField(max_length=300)
    delegacia_origem = models.CharField(max_length=100)
    comarca = models.CharField(max_length=100)
    
    investigador_principal = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='casos_principais')
    investigadores_apoio = models.ManyToManyField(Usuario, blank=True, related_name='casos_apoio')
    delegado_responsavel = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='casos_delegado')
    
    numero_inquerito = models.CharField(max_length=50, blank=True)
    numero_processo = models.CharField(max_length=50, blank=True)
    vara_judicial = models.CharField(max_length=100, blank=True)
    
    observacoes = models.TextField(blank=True)
    observacoes_internas = models.TextField(blank=True)  # Não aparecem em relatórios
    
    confidencial = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='casos_criados')
    
    class Meta:
        ordering = ['-data_abertura']
        indexes = [
            models.Index(fields=['numero_caso']),
            models.Index(fields=['status']),
            models.Index(fields=['data_ocorrencia']),
        ]
    
    def __str__(self):
        return f"{self.numero_caso} - {self.titulo}"

class EnvolvimentoCaso(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    TIPO_ENVOLVIMENTO_CHOICES = [
        ('suspeito', 'Suspeito'),
        ('vitima', 'Vítima'),
        ('testemunha', 'Testemunha'),
        ('informante', 'Informante'),
        ('outro', 'Outro'),
    ]
    
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='envolvimentos')
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name='envolvimentos')
    tipo_envolvimento = models.CharField(max_length=20, choices=TIPO_ENVOLVIMENTO_CHOICES)
    descricao = models.TextField(blank=True)
    data_envolvimento = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['caso', 'pessoa', 'tipo_envolvimento']
    
    def __str__(self):
        return f"{self.pessoa.nome_completo} - {self.tipo_envolvimento} - {self.caso.numero_caso}"

class EventoTimeline(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
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
    
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='eventos_timeline')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_hora = models.DateTimeField()
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)
    importancia = models.IntegerField(choices=IMPORTANCIA_CHOICES, default=2)
    
    investigador_responsavel = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    pessoas_envolvidas = models.ManyToManyField(Pessoa, blank=True)
    evidencias_relacionadas = models.ManyToManyField('evidencias.Evidencia', blank=True)
    
    localizacao = models.CharField(max_length=300, blank=True)
    coordenadas_lat = models.CharField(blank=True)
    coordenadas_lng = models.CharField(null=True, blank=True)
    
    confirmado = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, related_name='eventos_criados')
    
    class Meta:
        ordering = ['data_hora']
        indexes = [
            models.Index(fields=['caso', 'data_hora']),
            models.Index(fields=['tipo_evento']),
        ]
    
    def __str__(self):
        return f"{self.caso.numero_caso} - {self.titulo} - {self.data_hora}"
    
class Notificacao(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    TIPO_NOTIFICACAO_CHOICES = [
        ('caso_atribuido', 'Caso Atribuído'),
        ('prazo_vencendo', 'Prazo Vencendo'),
        ('evidencia_coletada', 'Evidência Coletada'),
        ('evento_timeline', 'Evento Timeline'),
        ('mensagem', 'Mensagem'),
        ('sistema', 'Sistema'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_NOTIFICACAO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, null=True, blank=True)
    
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_leitura = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"

class Comentario(models.Model):
    id = models.UUIDField(
      primary_key = True,
      default = uuid.uuid4,
      editable= False
    )
    
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    comentario = models.TextField()
    data_comentario = models.DateTimeField(auto_now_add=True)
    editado = models.BooleanField(default=False)
    data_edicao = models.DateTimeField(null=True, blank=True)
    
    # Privacidade
    interno = models.BooleanField(default=False)  # Comentário interno (não aparece em relatórios)
    
    class Meta:
        ordering = ['-data_comentario']
    
    def __str__(self):
        return f"{self.caso.numero_caso} - {self.autor.username} - {self.data_comentario}"
    

class Relatorio(models.Model):
    
    TIPO_RELATORIO_CHOICES = [
        ('investigacao', 'Relatório de Investigação'),
        ('final', 'Relatório Final'),
        ('pericia', 'Relatório de Perícia'),
        ('estatistico', 'Relatório Estatístico'),
        ('timeline', 'Relatório Timeline'),
        ('personalizado', 'Relatório Personalizado'),
    ]
    
    caso = models.ForeignKey(Caso, on_delete=models.CASCADE, related_name='relatorios', null=True, blank=True)
    tipo_relatorio = models.CharField(max_length=20, choices=TIPO_RELATORIO_CHOICES)
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    
    gerado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    data_geracao = models.DateTimeField(auto_now_add=True)
    assinado = models.BooleanField(default=False)
    data_assinatura = models.DateTimeField(null=True, blank=True)
    assinado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='relatorios_assinados')
    
    arquivo_pdf = models.FileField(upload_to='relatorios/', null=True, blank=True)
    
    class Meta:
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"{self.titulo} - {self.data_geracao}"