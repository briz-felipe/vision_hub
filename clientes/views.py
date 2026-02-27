from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cliente
from .forms import ClienteForm


@login_required
def lista_clientes(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    
    clientes = Cliente.objects.filter(ativo=True)
    if query:
        from django.db.models import Q
        clientes = clientes.filter(
            Q(nome__icontains=query) |
            Q(nome_fantasia__icontains=query) |
            Q(cpf__icontains=query) |
            Q(cnpj__icontains=query) |
            Q(email__icontains=query) |
            Q(telefone__icontains=query)
        )
    if tipo:
        clientes = clientes.filter(tipo_pessoa=tipo)
    
    context = {
        'clientes': clientes,
        'query': query,
        'tipo_filtro': tipo,
        'tipo_choices': Cliente.TipoPessoa.choices,
        'total_clientes': Cliente.objects.filter(ativo=True).count(),
        'total_pf': Cliente.objects.filter(ativo=True, tipo_pessoa=Cliente.TipoPessoa.FISICA).count(),
        'total_pj': Cliente.objects.filter(ativo=True, tipo_pessoa=Cliente.TipoPessoa.JURIDICA).count(),
    }
    return render(request, 'clientes/lista.html', context)


@login_required
def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=True)
            cliente.criado_por = request.user
            cliente.save()
            messages.success(request, f'Cliente "{cliente.nome}" cadastrado com sucesso!')
            return redirect('clientes:detalhe', pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {
        'form': form, 'titulo_pagina': 'Novo Cliente',
    })


@login_required
def detalhe_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    chamados = cliente.chamados.all()[:10]
    context = {
        'cliente': cliente,
        'chamados': chamados,
    }
    return render(request, 'clientes/detalhe.html', context)


@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes:detalhe', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {
        'form': form, 'cliente': cliente, 'titulo_pagina': 'Editar Cliente',
    })


@login_required
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.ativo = False
        cliente.save()
        messages.success(request, 'Cliente desativado com sucesso!')
        return redirect('clientes:lista')
    return render(request, 'clientes/confirmar_exclusao.html', {'cliente': cliente})
