from django.urls import path
from . import views
urlpatterns = [
    path('', views.Home, name='home'),
    path('login/', views.login_usuario, name='login'),
    #path('logout/', views.Logout, name='logout'),
    #path('teste/', views.Teste, name='teste')
    path('agendar/<int:servico_id>/', views.agendar_servico, name='agendar_servico'),
    #HTMX
    path('lista_profissionais/', views.lista_profissionais, name='lista_profissionais'),
    path('lista_servicos', views.lista_servicos, name='lista_servicos'),
    path('teste-dia-htmx/', views.teste_dia_htmx, name='teste_dia_htmx'),
    path('agenda-barbeiro-htmx/',views.agenda_barbeiro_htmx,name='agenda_barbeiro_htmx'),
    path('confirmar-agendamento/', views.confirmar_agendamento, name='confirmar_agendamento'),
    path('realizar_cadastro/', views.realizar_cadastro, name='realizar_cadastro'),
    path('cadastro/', views.cadastro_usuario, name='cadastro'),
    path('meus-agendamentos/', views.ver_agendamentos, name='meus_agendamentos'),
    path(
    'cancelar-agendamento/<int:agendamento_id>/',views.cancelar_agendamento,name='cancelar_agendamento'),
]