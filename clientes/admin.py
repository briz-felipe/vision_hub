from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'tipo_pessoa', 'cpf', 'cnpj', 'cidade', 'estado',
        'telefone', 'ativo', 'criado_em',
    )
    list_filter = ('tipo_pessoa', 'ativo', 'estado')
    search_fields = ('nome', 'nome_fantasia', 'cpf', 'cnpj', 'email', 'telefone')
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por')
    fieldsets = (
        ('Tipo', {'fields': ('tipo_pessoa', 'ativo')}),
        ('Identificação', {'fields': ('cpf', 'cnpj')}),
        ('Nome', {'fields': ('nome', 'nome_fantasia')}),
        ('Endereço', {
            'fields': ('cep', 'estado', 'cidade', 'bairro', 'logradouro', 'numero', 'complemento'),
        }),
        ('Contato', {'fields': ('telefone', 'email')}),
        ('Meta', {'fields': ('criado_por', 'criado_em', 'atualizado_em')}),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
