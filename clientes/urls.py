from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.lista_clientes, name='lista'),
    path('novo/', views.criar_cliente, name='criar'),
    path('<int:pk>/', views.detalhe_cliente, name='detalhe'),
    path('<int:pk>/editar/', views.editar_cliente, name='editar'),
    path('<int:pk>/excluir/', views.excluir_cliente, name='excluir'),
]
