"""
Serviços de negócio para o módulo de chamados.
Mantém a lógica fora das views / models.
"""
import os
from django.conf import settings
from django.db.models import Sum, Count
from django.utils import timezone

from .models import Chamado, Video


class ChamadoService:
    """Operações de alto nível sobre Chamados."""

    @staticmethod
    def criar_chamado(*, dados: dict, usuario) -> Chamado:
        chamado = Chamado(**dados, criado_por=usuario)
        chamado.save()
        return chamado

    @staticmethod
    def atualizar_chamado(chamado: Chamado, dados: dict) -> Chamado:
        for attr, value in dados.items():
            setattr(chamado, attr, value)
        chamado.save()
        return chamado

    @staticmethod
    def pesquisar(query: str, usuario=None):
        qs = Chamado.objects.all()
        if usuario:
            qs = qs.filter(criado_por=usuario)
        if query:
            qs = qs.filter(
                models_Q_titulo_descricao_cliente(query)
            )
        return qs

    @staticmethod
    def buscar_chamados(usuario, query='', status='', prioridade=''):
        qs = Chamado.objects.filter(criado_por=usuario)
        if query:
            from django.db.models import Q
            qs = qs.filter(
                Q(titulo__icontains=query)
                | Q(descricao__icontains=query)
                | Q(cliente__icontains=query)
                | Q(slug__icontains=query)
            )
        if status:
            qs = qs.filter(status=status)
        if prioridade:
            qs = qs.filter(prioridade=prioridade)
        return qs


class VideoService:
    """Operações de alto nível sobre Vídeos."""

    @staticmethod
    def validar_arquivo(arquivo) -> list[str]:
        erros = []
        ext = os.path.splitext(arquivo.name)[1].lower()
        if ext not in settings.ALLOWED_VIDEO_EXTENSIONS:
            erros.append(
                f'Extensão "{ext}" não permitida. '
                f'Use: {", ".join(settings.ALLOWED_VIDEO_EXTENSIONS)}'
            )
        if arquivo.size > settings.MAX_VIDEO_FILE_SIZE:
            max_mb = settings.MAX_VIDEO_FILE_SIZE / (1024 * 1024)
            erros.append(f'Arquivo excede o limite de {max_mb:.0f} MB.')
        return erros

    @staticmethod
    def salvar_video(*, chamado: Chamado, arquivo, usuario, descricao='') -> Video:
        video = Video(
            chamado=chamado,
            arquivo=arquivo,
            nome_original=arquivo.name,
            tamanho=arquivo.size,
            descricao=descricao,
            enviado_por=usuario,
        )
        video.save()
        return video

    @staticmethod
    def excluir_video(video: Video):
        if video.arquivo:
            video.arquivo.delete(save=False)
        video.delete()


class DashboardService:
    """Métricas para o dashboard."""

    @staticmethod
    def get_metricas(usuario):
        chamados = Chamado.objects.filter(criado_por=usuario)
        videos = Video.objects.filter(chamado__criado_por=usuario)

        total_chamados = chamados.count()
        chamados_abertos = chamados.filter(status='aberto').count()
        chamados_andamento = chamados.filter(status='em_andamento').count()
        chamados_resolvidos = chamados.filter(status='resolvido').count()
        chamados_fechados = chamados.filter(status='fechado').count()

        total_videos = videos.count()
        espaco_usado = videos.aggregate(total=Sum('tamanho'))['total'] or 0

        # Últimos chamados
        ultimos_chamados = chamados[:5]

        # Chamados por prioridade
        por_prioridade = {
            'baixa': chamados.filter(prioridade='baixa').count(),
            'media': chamados.filter(prioridade='media').count(),
            'alta': chamados.filter(prioridade='alta').count(),
            'critica': chamados.filter(prioridade='critica').count(),
        }

        return {
            'total_chamados': total_chamados,
            'chamados_abertos': chamados_abertos,
            'chamados_andamento': chamados_andamento,
            'chamados_resolvidos': chamados_resolvidos,
            'chamados_fechados': chamados_fechados,
            'total_videos': total_videos,
            'espaco_usado': espaco_usado,
            'espaco_formatado': DashboardService._formatar_tamanho(espaco_usado),
            'ultimos_chamados': ultimos_chamados,
            'por_prioridade': por_prioridade,
        }

    @staticmethod
    def _formatar_tamanho(size_bytes):
        if size_bytes == 0:
            return '0 B'
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'
