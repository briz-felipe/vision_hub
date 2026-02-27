from django.urls import path
from . import views

app_name = 'chamados'

urlpatterns = [
    # --- Área autenticada ---
    path('', views.lista_chamados, name='lista'),
    path('novo/', views.criar_chamado, name='criar'),
    path('<int:pk>/', views.detalhe_chamado, name='detalhe'),
    path('<int:pk>/editar/', views.editar_chamado, name='editar'),
    path('<int:pk>/excluir/', views.excluir_chamado, name='excluir'),
    path('<int:pk>/upload/', views.upload_video, name='upload_video'),
    path('<int:pk>/comentario/', views.adicionar_comentario, name='adicionar_comentario'),
    path('<int:pk>/status/', views.mudar_status, name='mudar_status'),
    path('video/<int:video_id>/excluir/', views.excluir_video, name='excluir_video'),

    # --- Área pública (compartilhamento) ---
    path('compartilhado/<slug:slug>/', views.chamado_compartilhado, name='compartilhado'),
    path('compartilhado/<slug:slug>/comentario/', views.adicionar_comentario_publico, name='adicionar_comentario_publico'),
]
