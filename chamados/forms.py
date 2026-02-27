from django import forms
from .models import Chamado, Video


class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = [
            'titulo', 'descricao', 'cliente',
            'status', 'prioridade',
            'tipo_compartilhamento', 'senha_compartilhamento', 'expira_em',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Ocorrência no Condomínio Solar',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Descreva a ocorrência...',
            }),
            'cliente': forms.Select(attrs={
                'class': 'form-select',
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'tipo_compartilhamento': forms.Select(attrs={
                'class': 'form-select', 'id': 'id_tipo_compartilhamento',
            }),
            'senha_compartilhamento': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Senha para acesso',
            }),
            'expira_em': forms.DateTimeInput(attrs={
                'class': 'form-control', 'type': 'datetime-local',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_compartilhamento')
        senha = cleaned_data.get('senha_compartilhamento')
        expira = cleaned_data.get('expira_em')

        if tipo == Chamado.TipoCompartilhamento.PROTEGIDO and not senha:
            self.add_error(
                'senha_compartilhamento',
                'Informe uma senha para compartilhamento protegido.',
            )
        if tipo == Chamado.TipoCompartilhamento.TEMPORARIO and not expira:
            self.add_error(
                'expira_em',
                'Informe a data de expiração para link temporário.',
            )
        return cleaned_data


class VideoUploadForm(forms.Form):
    arquivos = forms.FileField(
        label='Vídeos',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'video/*',
        }),
    )
    descricao = forms.CharField(
        label='Descrição dos vídeos',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Descrição opcional dos vídeos',
        }),
    )


class SenhaCompartilhamentoForm(forms.Form):
    senha = forms.CharField(
        label='Senha de acesso',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha do chamado',
        }),
    )


class ComentarioForm(forms.Form):
    texto = forms.CharField(
        label='Comentário',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Escreva seu comentário...',
        }),
    )
    autor_nome = forms.CharField(
        label='Seu nome (opcional)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Como deseja ser identificado?',
        }),
    )
