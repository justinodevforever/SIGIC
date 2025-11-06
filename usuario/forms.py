from django import forms
from .models import *
import string, secrets
import re
from decimal import Decimal

def gerar_senha():

    caracter = string.ascii_letters + string.digits + '@#$%!&%'


    return ''.join(secrets.choice(caracter) for _ in range(9))



class AliasForm(forms.ModelForm):
    
    class Meta:
        model = AliasPessoa
        fields = ['nome_alias', 'tipo_alias']
        widgets = {
            'nome_alias': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome alternativo ou apelido'
            }),
            'observacoes': forms.Select(attrs={
                'class': 'form-control',
            })
        }

class UserForm(forms.Form):


    username = forms.CharField(
        required=True,
        widget= forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    matricula = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departamento = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    nivel_acesso = forms.ChoiceField(
        label='Arquivo Confidencial',
        choices=Usuario.NIVEL_ACESSO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cargo = forms.ChoiceField(
        choices=Usuario.CARGO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bi = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    data_nascimento = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado_civil = forms.ChoiceField(
        choices=Usuario.ESTADO_CIVIL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    genero = forms.ChoiceField(
        choices=Usuario.GENERO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        
        
        if username:
            user = Usuario.objects.get(username=username)

            if user:

                self.add_error('username', 'Esse nome do usuário já existe!')

        return cleaned_data

    def save(self):

        password = gerar_senha()

        user = Usuario(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            departamento=self.cleaned_data['departamento'],
            email=self.cleaned_data['email'],
            nivel_acesso=self.cleaned_data['nivel_acesso'],
            matricula=self.cleaned_data['matricula'],
            telefone=self.cleaned_data['telefone'],
            cargo=self.cleaned_data['cargo'],
        )
        user.set_password(password)

        user.save()

        return user
    
class EditUserForm(forms.Form):
    

    username = forms.CharField(
        required=True,
        widget= forms.TextInput(attrs={'class': 'form-control'})
    )

    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    matricula = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departamento = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    cargo = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-control'})
    )
    nivel_acesso = forms.ChoiceField(
        choices=Usuario.NIVEL_ACESSO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cargo = forms.ChoiceField(
        choices=Usuario.CARGO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    bi = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    data_nascimento = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado_civil = forms.ChoiceField(
        choices=Usuario.ESTADO_CIVIL_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    genero = forms.ChoiceField(
        choices=Usuario.GENERO_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):

        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
       
        try:
            if username:
                user = Usuario.objects.get(username=username)

                if user and self.instance.id != user.id:

                    self.add_error('username', 'Esse nome do usuário já existe!')

        except Usuario.DoesNotExist:
            pass

        return cleaned_data
    
    def save(self):

        self.instance.username = self.cleaned_data['username']
        self.instance.last_name = self.cleaned_data['last_name']
        self.instance.first_name = self.cleaned_data['first_name']
        self.instance.departamento = self.cleaned_data['departamento']
        self.instance.cargo = self.cleaned_data['cargo']
        self.instance.nivel_acesso = self.cleaned_data['nivel_acesso']
        self.instance.email = self.cleaned_data['email']
        self.instance.matricula = self.cleaned_data['matricula']
        self.instance.estado_civil = self.cleaned_data['estado_civil']
        self.instance.genero = self.cleaned_data['genero']
        self.instance.bi = self.cleaned_data['bi']
        self.instance.telefone = self.cleaned_data['telefone']
        self.instance.is_active = self.cleaned_data['is_active']
        self.instance.ativo = self.cleaned_data['is_active']

        self.instance.save()

        return self.instance
    
class EditPessoaForm(forms.Form):

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
        choices= Pessoa.GENERO_CHOICES,
        required=True,
        widget= forms.Select(attrs={'class': 'form-control'}
    ))
    estado_civil = forms.ChoiceField(
        choices = Pessoa.ESTADO_CIVIL_CHOICES,
        required=True,
        widget= forms.Select( attrs={
            'class': 'form-control',
            }
    ))
   
    observacoes = forms.CharField(
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
    
    def save(self, pessoa=None):

        if pessoa:

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

            pessoa.nome_completo=self.cleaned_data['nome_completo']
            pessoa.nome_social=self.cleaned_data['nome_social']
            pessoa.bi=self.cleaned_data['bi']
            pessoa.data_nascimento=self.cleaned_data['data_nascimento']
            pessoa.genero=self.cleaned_data['genero']
            pessoa.estado_civil=self.cleaned_data['estado_civil']
            pessoa.cor_olhos=self.cleaned_data['cor_olhos']
            pessoa.altura=altura
            pessoa.peso=peso
            pessoa.cor_cabelo=self.cleaned_data['cor_cabelo']
            pessoa.profissao=self.cleaned_data['profissao']
            pessoa.escolaridade=self.cleaned_data['escolaridade']
            pessoa.nacionalidade=self.cleaned_data['nacionalidade']
            pessoa.telefone_principal=telefone_principal
            pessoa.telefone_secundario=telefone_secundario
            pessoa.email=self.cleaned_data['email']
            pessoa.observacoes=self.cleaned_data['observacoes']

            pessoa.save()

            alias = None
            endereco = None

            try:


                alias = AliasPessoa.objects.get(pessoa=pessoa)

                alias.pessoa=pessoa
                alias.tipo_alias=self.cleaned_data['tipo_alias']
                alias.nome_alias=self.cleaned_data['nome_alias']

                alias.save()

            except AliasPessoa.DoesNotExist:

                alias = AliasPessoa(
                    pessoa=pessoa,
                    tipo_alias=self.cleaned_data['tipo_alias'],
                    nome_alias=self.cleaned_data['nome_alias']
                )
                alias.save()

            try:
                endereco = Endereco.objects.get(pessoa=pessoa)

                endereco.pessoa=pessoa
                endereco.tipo=self.cleaned_data['tipo_endereco']
                endereco.logradouro=self.cleaned_data['logradouro']
                endereco.numero=self.cleaned_data['numero']
                endereco.complemento=self.cleaned_data['complemento']
                endereco.bairro=self.cleaned_data['bairro']
                endereco.ponto_referencia=self.cleaned_data['ponto_referencia']
                endereco.cidade=self.cleaned_data['cidade']
                endereco.estado=self.cleaned_data['estado']

                endereco.save()
                
            except Endereco.DoesNotExist:

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

            return pessoa, endereco, alias