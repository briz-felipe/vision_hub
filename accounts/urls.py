from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('mudar-senha/', views.mudar_senha, name='mudar_senha'),

    # Gestão de usuários
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/criar/', views.usuario_criar, name='usuario_criar'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/deletar/', views.usuario_deletar, name='usuario_deletar'),
]
