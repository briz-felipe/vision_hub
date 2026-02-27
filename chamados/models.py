import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Chamado(models.Model):
    """Representa um chamado / ocorrência de monitoramento."""

    class Status(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
        RESOLVIDO = 'resolvido', 'Resolvido'
        FECHADO = 'fechado', 'Fechado'

    class Prioridade(models.TextChoices):
        BAIXA = 'baixa', 'Baixa'
        MEDIA = 'media', 'Média'
        ALTA = 'alta', 'Alta'
        CRITICA = 'critica', 'Crítica'

    class TipoCompartilhamento(models.TextChoices):
        PUBLICO = 'publico', 'Link Público'
        TEMPORARIO = 'temporario', 'Link Temporário'
        PROTEGIDO = 'protegido', 'Protegido por Senha'

    # Identificação
    slug = models.SlugField(
        max_length=64, unique=True, editable=False, db_index=True,
    )
    titulo = models.CharField('Título', max_length=200)
    descricao = models.TextField('Descrição', blank=True)

    # Localização / cliente
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='chamados',
        verbose_name='Cliente',
    )

    # Classificação
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ABERTO,
    )
    prioridade = models.CharField(
        max_length=20, choices=Prioridade.choices, default=Prioridade.MEDIA,
    )

    # Compartilhamento
    tipo_compartilhamento = models.CharField(
        'Tipo de Compartilhamento',
        max_length=20,
        choices=TipoCompartilhamento.choices,
        default=TipoCompartilhamento.PUBLICO,
    )
    senha_compartilhamento = models.CharField(
        'Senha do Link', max_length=128, blank=True,
        help_text='Necessário quando o tipo é "Protegido por Senha".',
    )
    expira_em = models.DateTimeField(
        'Expira em', null=True, blank=True,
        help_text='Necessário quando o tipo é "Link Temporário".',
    )

    # Meta
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chamados',
        verbose_name='Criado por',
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Chamado'
        verbose_name_plural = 'Chamados'

    def __str__(self):
        return f'#{self.pk} — {self.titulo}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

    # ---------- helpers ----------
    @property
    def link_compartilhamento(self):
        return f'/chamados/compartilhado/{self.slug}/'

    @property
    def link_expirado(self):
        if self.tipo_compartilhamento != self.TipoCompartilhamento.TEMPORARIO:
            return False
        if self.expira_em is None:
            return False
        return timezone.now() > self.expira_em

    @property
    def total_videos(self):
        return self.videos.count()

    @property
    def tamanho_total(self):
        """Retorna o tamanho total dos vídeos em bytes."""
        return self.videos.aggregate(total=models.Sum('tamanho'))['total'] or 0

    @property
    def cor_prioridade(self):
        cores = {
            'baixa': '#22c55e',
            'media': '#f59e0b',
            'alta': '#f97316',
            'critica': '#ef4444',
        }
        return cores.get(self.prioridade, '#6b7280')

    @property
    def cor_status(self):
        cores = {
            'aberto': '#7c3aed',
            'em_andamento': '#2563eb',
            'resolvido': '#16a34a',
            'fechado': '#6b7280',
        }
        return cores.get(self.status, '#6b7280')


def video_upload_path(instance, filename):
    return f'videos/chamado_{instance.chamado_id}/{filename}'


class Video(models.Model):
    """Arquivo de vídeo anexado a um chamado."""

    chamado = models.ForeignKey(
        Chamado, on_delete=models.CASCADE, related_name='videos',
    )
    arquivo = models.FileField('Arquivo de Vídeo', upload_to=video_upload_path)
    nome_original = models.CharField('Nome Original', max_length=255)
    tamanho = models.BigIntegerField('Tamanho (bytes)', default=0)
    descricao = models.CharField('Descrição do vídeo', max_length=300, blank=True)
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Enviado por',
    )
    enviado_em = models.DateTimeField('Enviado em', auto_now_add=True)

    class Meta:
        ordering = ['-enviado_em']
        verbose_name = 'Vídeo'
        verbose_name_plural = 'Vídeos'

    def __str__(self):
        return self.nome_original

    @property
    def extensao(self):
        import os
        return os.path.splitext(self.nome_original)[1].lower()

    @property
    def tamanho_formatado(self):
        """Mostra o tamanho de forma legível (KB, MB, GB)."""
        size = self.tamanho
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f'{size:.1f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'


class Comentario(models.Model):
    """Comentário em um chamado."""

    chamado = models.ForeignKey(
        Chamado, on_delete=models.CASCADE, related_name='comentarios',
    )
    texto = models.TextField('Comentário')
    autor_nome = models.CharField(
        'Nome do Autor',
        max_length=100,
        blank=True,
        help_text='Identificação opcional para visitantes externos',
    )
    autor_usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuário',
    )
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)

    class Meta:
        ordering = ['criado_em']
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'

    def __str__(self):
        autor = self.autor_usuario.username if self.autor_usuario else self.autor_nome or 'Anônimo'
        return f'{autor} em {self.criado_em.strftime("%d/%m/%Y %H:%M")}'

    @property
    def autor_display(self):
        if self.autor_usuario:
            return f'{self.autor_usuario.get_full_name() or self.autor_usuario.username} (Proceder)'
        return self.autor_nome or 'Visitante'
