from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime, date
from django.utils import timezone
from .models import *
from decimal import Decimal

class EvidenciaForm(forms.Form):

    STATUS_CHOICES = [
        ('coletada', 'Coletada'),
        ('em_analise', 'Em Análise'),
        ('analisada', 'Analisada'),
        ('devolvida', 'Devolvida'),
        ('destruida', 'Destruída'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))

    dimensoes = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    estado_conservacao = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    material = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    cor = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    local_armazenamento = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    numero_lacre = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    local_coleta = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    data_coleta = forms.DateTimeField(
        required=True,
        widget= forms.DateTimeInput( attrs={'class': 'form-control'}
    ))
    
    tipo = forms.ModelChoiceField(
        queryset=TipoEvidencia.objects.none(),
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    coletado_por = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    custodia_atual = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    peso = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=3,
        initial=Decimal("0.000"),
        widget= forms.NumberInput( attrs={'class': 'form-control',
        "step":"0.001"},
    ))
    valor_estimado = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        initial=Decimal("0.00"),
        widget= forms.NumberInput( attrs={'class': 'form-control',
        "step":"0.001"},
    ))

    descricao = forms.CharField(
        required=True,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    observacoes = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        usuarios = Usuario.objects.filter(
            cargo__in=['investigador', 'delegado', 'perito']
        ).order_by('first_name', 'last_name')

        self.fields['coletado_por'].queryset = usuarios
        self.fields['custodia_atual'].queryset = usuarios
        
        self.fields['tipo'].queryset = TipoEvidencia.objects.filter(ativo=True)
    
    def clean_numero_evidencia(self):
        numero = self.cleaned_data.get('numero_evidencia')
        if numero:
           
            query = Evidencia.objects.filter(numero_evidencia=numero)
            if self.instance.pk:
                Query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise ValidationError('Este número de evidência já existe.')
        
        return numero
    
    def save(self, evidencia=None):

        ano_atual = timezone.now().year

        if evidencia is None:

            numero = 0

            ultimo_evidencia = Evidencia.objects.filter(
                numero_evidencia__startswith=str(ano_atual)
            ).order_by('data_criacao').last()

            if ultimo_evidencia:
                v = ultimo_evidencia.numero_evidencia.split('-')[1].split('#')
                numero = f'#{int(v[1]) + 1}'

            else:
                numero = f'#{1}'

            numero_evidencia = f'{ano_atual}-{numero}'

            ev = Evidencia(
                numero_evidencia=numero_evidencia,
                caso=self.instance,
                coletado_por=self.cleaned_data['coletado_por'],
                cor=self.cleaned_data['cor'],
                custodia_atual=self.cleaned_data[ 'custodia_atual'],
                data_coleta=self.cleaned_data['data_coleta'],
                descricao=self.cleaned_data['descricao'],
                dimensoes=self.cleaned_data['dimensoes'],
                estado_conservacao=self.cleaned_data['estado_conservacao'],
                local_armazenamento=self.cleaned_data['local_armazenamento'],
                local_coleta=self.cleaned_data['local_coleta'],
                material=self.cleaned_data['material'],
                numero_lacre=self.cleaned_data['numero_lacre'],
                observacoes=self.cleaned_data['observacoes'],
                peso=self.cleaned_data['peso'],
                status=self.cleaned_data['status'],
                tipo=self.cleaned_data['tipo'],
                valor_estimado=self.cleaned_data['valor_estimado'],
            )

            ev.save()

            return ev
        
        else:

            evidencia.coletado_por=self.cleaned_data['coletado_por']
            evidencia.cor=self.cleaned_data['cor']
            evidencia.custodia_atual=self.cleaned_data[ 'custodia_atual']
            evidencia.data_coleta=self.cleaned_data['data_coleta']
            evidencia.descricao=self.cleaned_data['descricao']
            evidencia.dimensoes=self.cleaned_data['dimensoes']
            evidencia.estado_conservacao=self.cleaned_data['estado_conservacao']
            evidencia.local_armazenamento=self.cleaned_data['local_armazenamento']
            evidencia.local_coleta=self.cleaned_data['local_coleta']
            evidencia.material=self.cleaned_data['material']
            evidencia.numero_lacre=self.cleaned_data['numero_lacre']
            evidencia.observacoes=self.cleaned_data['observacoes']
            evidencia.peso=self.cleaned_data['peso']
            evidencia.status=self.cleaned_data['status']
            evidencia.tipo=self.cleaned_data['tipo']
            evidencia.valor_estimado=self.cleaned_data['valor_estimado']

            evidencia.save()

        return evidencia

class PericiaForm(forms.Form):

    TIPOS = [
        ('DNA', 'DNA'),
        ('BALISTICA', 'Balística'),
        ('TOXICOLOGIA', 'Toxicologia'),
        ('DIGITAIS', 'Digitais')
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPOS,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))

    resultado = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    conclusao = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))

    numero_evidencia = forms.CharField(
        required=False,
        max_length=100,
        widget= forms.TextInput( attrs={'class': 'form-control'},
    ))

    def clean(self):

        cleaned_data = super().clean()

        try:
            if not Evidencia.objects.get(numero_evidencia=cleaned_data.get('numero_evidencia')):
                self.add_error('numero_evidencia', 'Número da evidência inválido')
        
        except Exception as e:
            self.add_error('numero_evidencia', 'Número da evidência inválido')

        return cleaned_data
    
    def save(self, pericia=None):

        if pericia is None:

            evidencia = Evidencia.objects.get(
                numero_evidencia=self.cleaned_data['numero_evidencia']
                )

            peri = Pericia(
                evidencia=evidencia,
                resultado=self.cleaned_data['resultado'],
                conclusao=self.cleaned_data['conclusao'],
                tipo=self.cleaned_data[ 'tipo'],
            )

            return peri
        
        else:

            evidencia = Evidencia.objects.get(numero_evidencia=self.cleaned_data['numero_evidencia'])

            pericia.evidencia=evidencia
            pericia.resultado=self.cleaned_data['resultado']
            pericia.conclusao=self.cleaned_data['conclusao']
            pericia.tipo=self.cleaned_data[ 'tipo']
            

            pericia.save()

            return  pericia


class CadeiaCustodiaForm(forms.Form):

    TIPO_MOVIMENTACAO_CHOICES = [
        ('coleta', 'Coleta'),
        ('transferencia', 'Transferência'),
        ('analise', 'Análise'),
        ('devolucao', 'Devolução'),
        ('armazenamento', 'Armazenamento'),
        ('destruicao', 'Destruição'),
    ]
    
    tipo_movimentacao = forms.ChoiceField(
        choices=TIPO_MOVIMENTACAO_CHOICES,
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))

    local_destino = forms.CharField(
        required=True,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    local_origem = forms.CharField(
        required=False,
        widget= forms.TextInput( attrs={'class': 'form-control'}
    ))
    
    responsavel_anterior = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))
    responsavel_atual = forms.ModelChoiceField(
        queryset=Usuario.objects.none(),
        required=True,
        widget= forms.Select( attrs={'class': 'form-control'}
    ))

    motivo = forms.CharField(
        required=True,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    observacoes = forms.CharField(
        required=False,
        widget= forms.Textarea( attrs={'class': 'form-control'}
    ))
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        usuarios = Usuario.objects.filter(
            cargo__in=['investigador', 'delegado', 'perito']
        ).order_by('first_name', 'last_name')
        
        self.fields['responsavel_anterior'].queryset = usuarios
        self.fields['responsavel_atual'].queryset = usuarios
    
    def save(self, evidencia=None):

        cust = CadeiaCustomia(
            evidencia=self.instance,
            tipo_movimentacao=self.cleaned_data['tipo_movimentacao'],
            local_destino=self.cleaned_data['local_destino'],
            local_origem=self.cleaned_data['local_origem'],
            responsavel_anterior=self.cleaned_data['responsavel_anterior'],
            responsavel_atual=self.cleaned_data['responsavel_atual'],
            motivo=self.cleaned_data['motivo'],
            observacoes=self.cleaned_data['observacoes'],
        )

        cust.save()

        return cust

# class ArquivoForm(forms.ModelForm):
    
#     class Meta:
#         model = Arquivo
#         fields = ['nome_arquivo', 'descricao', 'tipo_arquivo', 'arquivo', 'tags']
#         widgets = {
#             'nome_arquivo': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Nome do arquivo'
#             }),
#             'descricao': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'Descrição do arquivo'
#             }),
#             'tipo_arquivo': forms.Select(attrs={
#                 'class': 'form-control'
#             }),
#             'arquivo': forms.FileInput(attrs={
#                 'class': 'form-control-file'
#             }),
#             'tags': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'placeholder': 'Tags separadas por vírgula'
#             })
#         }
    
#     def clean_arquivo(self):
#         arquivo = self.cleaned_data.get('arquivo')
#         if arquivo:
#             # Verificar tamanho do arquivo (limite de 50MB)
#             if arquivo.size > 50 * 1024 * 1024:
#                 raise ValidationError('O arquivo não pode ser maior que 50MB.')
            
#             # Verificar extensões permitidas
#             extensoes_permitidas = [
#                 '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
#                 '.txt', '.rtf', '.jpg', '.jpeg', '.png', '.gif', '.bmp',
#                 '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.zip', '.rar'
#             ]
            
#             # Nome_arquivo = arquivo.name.lower()
#             # if not any(nome_arquivo.endswith(ext) for ext in exit

