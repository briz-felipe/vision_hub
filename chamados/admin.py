from django.contrib import admin
from .models import Chamado, Comentario, Video


class VideoInline(admin.TabularInline):
    model = Video
    extra = 0
    readonly_fields = ('nome_original', 'tamanho', 'enviado_por', 'enviado_em')


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ('autor_display', 'texto', 'criado_em')
    fields = ('autor_display', 'texto', 'criado_em')


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'titulo', 'cliente', 'status', 'prioridade',
        'tipo_compartilhamento', 'criado_por', 'criado_em',
    )
    list_filter = ('status', 'prioridade', 'tipo_compartilhamento')
    search_fields = ('titulo', 'descricao', 'cliente__nome', 'slug')
    readonly_fields = ('slug', 'criado_em', 'atualizado_em')
    inlines = [VideoInline, ComentarioInline]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('nome_original', 'chamado', 'tamanho', 'enviado_por', 'enviado_em')
    list_filter = ('enviado_em',)
    search_fields = ('nome_original', 'descricao')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('chamado', 'autor_display', 'texto_truncado', 'criado_em')
    list_filter = ('criado_em',)
    search_fields = ('texto', 'autor_nome', 'autor_usuario__username')
    readonly_fields = ('criado_em',)
    
    def texto_truncado(self, obj):
        return obj.texto[:50] + '...' if len(obj.texto) > 50 else obj.texto
    texto_truncado.short_description = 'Texto'
