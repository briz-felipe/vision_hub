from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from chamados.services import DashboardService


@login_required
def index(request):
    metricas = DashboardService.get_metricas(request.user)
    return render(request, 'dashboard/index.html', metricas)
