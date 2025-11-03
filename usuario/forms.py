from django import forms
from .models import *
import string, secrets

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