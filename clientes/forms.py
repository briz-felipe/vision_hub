from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'tipo_pessoa', 'cpf', 'cnpj', 'nome', 'nome_fantasia',
            'cep', 'estado', 'cidade', 'bairro', 'logradouro', 'numero', 'complemento',
            'telefone', 'email',
        ]
        widgets = {
            'tipo_pessoa': forms.Select(attrs={
                'class': 'form-select', 'id': 'id_tipo_pessoa',
            }),
            'cpf': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '000.000.000-00',
                'maxlength': '14', 'id': 'id_cpf',
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '00.000.000/0000-00',
                'maxlength': '18', 'id': 'id_cnpj',
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome completo ou Razão Social',
            }),
            'nome_fantasia': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome Fantasia (opcional)',
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '00000-000',
                'maxlength': '9', 'id': 'id_cep',
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control bg-light', 'readonly': True, 'id': 'id_estado',
                'placeholder': 'Preenchido automaticamente',
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control bg-light', 'readonly': True, 'id': 'id_cidade',
                'placeholder': 'Preenchido automaticamente',
            }),
            'bairro': forms.TextInput(attrs={
                'class': 'form-control bg-light', 'readonly': True, 'id': 'id_bairro',
                'placeholder': 'Preenchido automaticamente',
            }),
            'logradouro': forms.TextInput(attrs={
                'class': 'form-control bg-light', 'readonly': True, 'id': 'id_logradouro',
                'placeholder': 'Preenchido automaticamente',
            }),
            'numero': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nº', 'id': 'id_numero',
            }),
            'complemento': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Bloco, Apto, sala...',
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '(00) 00000-0000',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'email@exemplo.com',
            }),
            # 'ativo' intentionally excluded from the form to avoid accidental
            # deactivation when the field is not rendered in the template.
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo_pessoa')
        cpf = cleaned_data.get('cpf')
        cnpj = cleaned_data.get('cnpj')

        if not cpf and not cnpj:
            raise forms.ValidationError('Informe pelo menos CPF ou CNPJ.')
        
        if tipo == Cliente.TipoPessoa.FISICA:
            if not cpf:
                self.add_error('cpf', 'CPF é obrigatório para Pessoa Física.')
        elif tipo == Cliente.TipoPessoa.JURIDICA:
            if not cnpj:
                self.add_error('cnpj', 'CNPJ é obrigatório para Pessoa Jurídica.')

        return cleaned_data
