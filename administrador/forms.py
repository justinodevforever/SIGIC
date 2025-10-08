from django import forms
from usuario.models import *
import string, secrets

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
        email = cleaned_data.get('email')
        cargo = cleaned_data.get('cargo')
        departamento = cleaned_data.get('departamento')
        telefone = cleaned_data.get('telefone')
        matricula = cleaned_data.get('matricula')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        nivel_acesso = cleaned_data.get('nivel_acesso')
        
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

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        cargo = cleaned_data.get('cargo')
        departamento = cleaned_data.get('departamento')
        telefone = cleaned_data.get('telefone')
        matricula = cleaned_data.get('matricula')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        nivel_acesso = cleaned_data.get('nivel_acesso')
       
        
        # if username:
        #     user = Usuario.objects.get(username=username)

        #     if user:

        #         self.add_error('username', 'Esse nome do usuário já existe!')

        return cleaned_data

 