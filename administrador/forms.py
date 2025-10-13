from django import forms
from usuario.models import *
import string, secrets
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def gerar_senha():

    caracter = string.ascii_letters + string.digits + '@#$%!&%'


    return ''.join(secrets.choice(caracter) for _ in range(9))

class PessoaForm(forms.ModelForm):
    
    class Meta:
        Model = Pessoa
        Fields = [
            'nome_completo', 'nome_social', 'cpf', 'rg', 'data_nascimento',
            'nacionalidade', 'naturalidade', 'estado_civil', 'profissao',
            'escolaridade', 'telefone', 'email', 'observacoes'
        ]
        Widgets = {
            'nome_completo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
            'nome_social': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome social (opcional)'
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '000.000.000-00'
            }),
            'rg': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'RG'
            }),
            'data_nascimento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nacionalidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nacionalidade'
            }),
            'naturalidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Naturalidade'
            }),
            'estado_civil': forms.Select(attrs={
                'class': 'form-control'
            }),
            'profissao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Profissão'
            }),
            'escolaridade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(00) 00000-0000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemplo.com'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações'
            })
        }
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            # Remove formatação
            cpf = ''.join(filter(str.isdigit, cpf))
            
            # Verifica se já existe (exceto para a própria pessoa em edição)
            query = Pessoa.objects.filter(cpf=cpf)
            if self.instance.pk:
                query = query.exclude(pk=self.instance.pk)
            
            if query.exists():
                raise ValidationError('Este CPF já está cadastrado.')
        
        return cpf
    
    def clean_data_nascimento(self):
        data = self.cleaned_data.get('data_nascimento')
        if data and data > date.today():
            raise ValidationError('A data de nascimento não pode ser futura.')
        
        return data

class EnderecoForm(forms.ModelForm):
    
    class Meta:
        model = Endereco
        fields = [
            'tipo', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'estado'
        ]
        Widgets = {
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'logradouro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rua, avenida, etc.'
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número'
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apartamento, bloco, etc.'
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Bairro'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control'
            })
        }


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
        required=True,
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
    nivel_acesso = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')

        
        try:
            if username:
                user = Usuario.objects.get(username=username)

            if user:

                return self.add_error('username', 'Esse nome do usuário já existe!')
                
        except Usuario.DoesNotExist:
            pass

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

        assunto = "SISTEMA INTEGRAL DE GESTÃO DE INVESTIGAÇÃO CRIMINAL"
        texto_simples = f"Olá {user.get_full_name} foi criada uma conta para ti no sistema de investigação criminal"
        html_conteudo = render_to_string('emails/email_user.html', {'nome': user.get_full_name, 'password': password, 'link': settings.BASE_URL,
                                                                    'username': user.username})

        email_msg = EmailMultiAlternatives(
            assunto,
            texto_simples,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        email_msg.attach_alternative(html_conteudo, "text/html")
        email_msg.send()

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
        required=True,
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
    nivel_acesso = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-control'})
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

 