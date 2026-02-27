from django.conf import settings
from django.db import models


class Cliente(models.Model):
    """Cliente que pode ser Pessoa Física ou Jurídica."""

    class TipoPessoa(models.TextChoices):
        FISICA = 'pf', 'Pessoa Física'
        JURIDICA = 'pj', 'Pessoa Jurídica'

    # Identificação
    tipo_pessoa = models.CharField(
        'Tipo de Pessoa',
        max_length=2,
        choices=TipoPessoa.choices,
        default=TipoPessoa.FISICA,
    )
    cpf = models.CharField('CPF', max_length=14, blank=True, db_index=True)
    cnpj = models.CharField('CNPJ', max_length=18, blank=True, db_index=True)
    
    # Nome
    nome = models.CharField('Nome / Razão Social', max_length=200)
    nome_fantasia = models.CharField('Nome Fantasia', max_length=200, blank=True)
    
    # Endereço
    cep = models.CharField('CEP', max_length=9, blank=True)
    estado = models.CharField('Estado', max_length=2, blank=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True)
    logradouro = models.CharField('Logradouro', max_length=200, blank=True)
    numero = models.CharField('Número', max_length=20, blank=True)
    complemento = models.CharField('Complemento', max_length=200, blank=True)
    
    # Contato
    telefone = models.CharField('Telefone', max_length=20, blank=True)
    email = models.EmailField('E-mail', blank=True)
    
    # Meta
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='clientes_criados',
        verbose_name='Criado por',
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        if self.tipo_pessoa == self.TipoPessoa.JURIDICA and self.nome_fantasia:
            return f'{self.nome_fantasia} ({self.cnpj})'
        return f'{self.nome} ({self.cpf or self.cnpj})'

    @property
    def documento(self):
        return self.cnpj if self.tipo_pessoa == self.TipoPessoa.JURIDICA else self.cpf

    @property
    def endereco_completo(self):
        partes = [
            self.logradouro,
            self.numero,
            self.complemento,
            self.bairro,
            f'{self.cidade}/{self.estado}' if self.cidade and self.estado else '',
            f'CEP: {self.cep}' if self.cep else '',
        ]
        return ', '.join(filter(None, partes))

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.cpf and not self.cnpj:
            raise ValidationError('Informe pelo menos CPF ou CNPJ.')
        if self.tipo_pessoa == self.TipoPessoa.FISICA and not self.cpf:
            raise ValidationError('CPF é obrigatório para Pessoa Física.')
        if self.tipo_pessoa == self.TipoPessoa.JURIDICA and not self.cnpj:
            raise ValidationError('CNPJ é obrigatório para Pessoa Jurídica.')
