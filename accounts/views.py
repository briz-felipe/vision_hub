from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from .forms import LoginForm, RegistroForm, MudarSenhaForm, UsuarioForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.username}!')
            return redirect('dashboard:index')
    else:
        form = RegistroForm()
    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def mudar_senha(request):
    if request.method == 'POST':
        form = MudarSenhaForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('dashboard:index')
    else:
        form = MudarSenhaForm(request.user)
    return render(request, 'accounts/mudar_senha.html', {'form': form})


# ── Gestão de Usuários ─────────────────────────────
@login_required
def usuario_lista(request):
    q = request.GET.get('q', '').strip()
    usuarios = User.objects.all().order_by('-date_joined')
    if q:
        usuarios = usuarios.filter(
            models_Q(username__icontains=q)
            | models_Q(first_name__icontains=q)
            | models_Q(last_name__icontains=q)
            | models_Q(email__icontains=q)
        )
    return render(request, 'accounts/usuario_lista.html', {
        'usuarios': usuarios,
        'query': q,
        'total_usuarios': User.objects.count(),
        'total_ativos': User.objects.filter(is_active=True).count(),
        'total_staff': User.objects.filter(is_staff=True).count(),
    })


@login_required
def usuario_criar(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('accounts:usuario_lista')
    else:
        form = UsuarioForm()
    return render(request, 'accounts/usuario_form.html', {
        'form': form,
        'titulo_pagina': 'Novo Usuário',
    })


@login_required
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('accounts:usuario_lista')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'accounts/usuario_form.html', {
        'form': form,
        'titulo_pagina': 'Editar Usuário',
        'usuario_obj': usuario,
    })


@login_required
def usuario_deletar(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if usuario == request.user:
            messages.error(request, 'Você não pode excluir seu próprio usuário.')
            return redirect('accounts:usuario_lista')
        usuario.delete()
        messages.success(request, f'Usuário "{usuario.username}" excluído.')
        return redirect('accounts:usuario_lista')
    return render(request, 'accounts/usuario_confirmar_exclusao.html', {
        'usuario_obj': usuario,
    })


# Helper – avoid importing models.Q at top level name clash
from django.db.models import Q as models_Q
