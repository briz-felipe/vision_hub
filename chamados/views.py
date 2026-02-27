from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ChamadoForm, ComentarioForm, SenhaCompartilhamentoForm, VideoUploadForm
from .models import Chamado, Comentario, Video
from .services import ChamadoService, VideoService


# ─────────────────── LISTA ───────────────────
@login_required
def lista_chamados(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    prioridade = request.GET.get('prioridade', '')

    chamados = ChamadoService.buscar_chamados(
        usuario=request.user,
        query=query,
        status=status,
        prioridade=prioridade,
    )

    context = {
        'chamados': chamados,
        'query': query,
        'status_filtro': status,
        'prioridade_filtro': prioridade,
        'status_choices': Chamado.Status.choices,
        'prioridade_choices': Chamado.Prioridade.choices,
    }
    return render(request, 'chamados/lista.html', context)


# ─────────────────── CRIAR ───────────────────
@login_required
def criar_chamado(request):
    if request.method == 'POST':
        form = ChamadoForm(request.POST)
        if form.is_valid():
            chamado = ChamadoService.criar_chamado(
                dados=form.cleaned_data,
                usuario=request.user,
            )
            messages.success(request, f'Chamado #{chamado.pk} criado com sucesso!')
            return redirect('chamados:detalhe', pk=chamado.pk)
    else:
        form = ChamadoForm()
    return render(request, 'chamados/form.html', {'form': form, 'titulo_pagina': 'Novo Chamado'})


# ─────────────────── DETALHE ───────────────────
@login_required
def detalhe_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk, criado_por=request.user)
    videos = chamado.videos.all()
    video_form = VideoUploadForm()
    comentarios = chamado.comentarios.all()
    comentario_form = ComentarioForm()
    share_url = request.build_absolute_uri(chamado.link_compartilhamento)

    context = {
        'chamado': chamado,
        'videos': videos,
        'video_form': video_form,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
        'share_url': share_url,
        'status_choices': Chamado.Status.choices,
    }
    return render(request, 'chamados/detalhe.html', context)


# ─────────────────── EDITAR ───────────────────
@login_required
def editar_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk, criado_por=request.user)
    if request.method == 'POST':
        form = ChamadoForm(request.POST, instance=chamado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chamado atualizado com sucesso!')
            return redirect('chamados:detalhe', pk=chamado.pk)
    else:
        form = ChamadoForm(instance=chamado)
    return render(request, 'chamados/form.html', {
        'form': form, 'chamado': chamado, 'titulo_pagina': 'Editar Chamado',
    })


# ─────────────────── EXCLUIR ───────────────────
@login_required
def excluir_chamado(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk, criado_por=request.user)
    if request.method == 'POST':
        for video in chamado.videos.all():
            VideoService.excluir_video(video)
        chamado.delete()
        messages.success(request, 'Chamado excluído com sucesso!')
        return redirect('chamados:lista')
    return render(request, 'chamados/confirmar_exclusao.html', {'chamado': chamado})


# ─────────────────── UPLOAD VÍDEO ───────────────────
@login_required
def upload_video(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk, criado_por=request.user)
    if request.method == 'POST':
        arquivos = request.FILES.getlist('arquivos')
        descricao = request.POST.get('descricao', '')
        if arquivos:
            erros_total = []
            salvos = 0
            for arq in arquivos:
                erros = VideoService.validar_arquivo(arq)
                if erros:
                    erros_total.extend(erros)
                else:
                    VideoService.salvar_video(
                        chamado=chamado,
                        arquivo=arq,
                        usuario=request.user,
                        descricao=descricao,
                    )
                    salvos += 1
            if salvos:
                messages.success(request, f'{salvos} vídeo(s) enviado(s) com sucesso!')
            for e in erros_total:
                messages.error(request, e)
        else:
            messages.error(request, 'Selecione ao menos um arquivo de vídeo.')
    return redirect('chamados:detalhe', pk=pk)


# ─────────────────── EXCLUIR VÍDEO ───────────────────
@login_required
def excluir_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id, chamado__criado_por=request.user)
    chamado_pk = video.chamado_id
    if request.method == 'POST':
        VideoService.excluir_video(video)
        messages.success(request, 'Vídeo excluído com sucesso!')
    return redirect('chamados:detalhe', pk=chamado_pk)


# ─────────────────── COMPARTILHADO (PÚBLICO) ───────────────────
def chamado_compartilhado(request, slug):
    chamado = get_object_or_404(Chamado, slug=slug)

    # Verificar expiração
    if chamado.link_expirado:
        return render(request, 'chamados/link_expirado.html', {'chamado': chamado})

    # Verificar senha
    if chamado.tipo_compartilhamento == Chamado.TipoCompartilhamento.PROTEGIDO:
        session_key = f'chamado_auth_{chamado.pk}'
        if not request.session.get(session_key):
            if request.method == 'POST':
                form = SenhaCompartilhamentoForm(request.POST)
                if form.is_valid():
                    if form.cleaned_data['senha'] == chamado.senha_compartilhamento:
                        request.session[session_key] = True
                    else:
                        messages.error(request, 'Senha incorreta.')
                        return render(request, 'chamados/senha_acesso.html', {
                            'form': form, 'chamado': chamado,
                        })
            else:
                form = SenhaCompartilhamentoForm()
                return render(request, 'chamados/senha_acesso.html', {
                    'form': form, 'chamado': chamado,
                })

    videos = chamado.videos.all()
    comentarios = chamado.comentarios.all()
    comentario_form = ComentarioForm()
    return render(request, 'chamados/compartilhado.html', {
        'chamado': chamado,
        'videos': videos,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
    })


# ─────────────────── ADICIONAR COMENTÁRIO ───────────────────
@login_required
def adicionar_comentario(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk, criado_por=request.user)
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        if texto:
            Comentario.objects.create(
                chamado=chamado,
                texto=texto,
                autor_usuario=request.user,
            )
            messages.success(request, 'Comentário adicionado!')
    return redirect('chamados:detalhe', pk=pk)


# ─────────────────── COMENTÁRIO PÚBLICO ───────────────────
def adicionar_comentario_publico(request, slug):
    chamado = get_object_or_404(Chamado, slug=slug)
    if request.method == 'POST':
        texto = request.POST.get('texto', '').strip()
        autor_nome = request.POST.get('autor_nome', '').strip()
        if texto:
            Comentario.objects.create(
                chamado=chamado,
                texto=texto,
                autor_nome=autor_nome,
            )
            messages.success(request, 'Comentário adicionado!')
    return redirect('chamados:compartilhado', slug=slug)


# ─────────────────── MUDAR STATUS ───────────────────
@login_required
def mudar_status(request, pk):
    chamado = get_object_or_404(Chamado, pk=pk, criado_por=request.user)
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in dict(Chamado.Status.choices):
            chamado.status = novo_status
            chamado.save()
            messages.success(request, f'Status alterado para "{chamado.get_status_display()}"!')
    return redirect('chamados:detalhe', pk=pk)
