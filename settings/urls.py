from django.urls import path

from .views import *


urlpatterns = [
    path('tool_sistem/', confg, name='confg'),
    path('secao_geral/', secao_geral, name='secao_geral'),
    path('secao_notificacao/', secao_notificacao, name='secao_notificacao'),
    path('secao_relatorio/', secao_relatorio, name='secao_relatorio'),
    path('secao_seguranca/', secao_seguranca, name='secao_seguranca'),
    path('secao_sistema/', secao_sistema, name='secao_sistema'),
    path('secao_usuario/', secao_usuario, name='secao_usuario'),

    path('logs_auditorio/', logs_auditorio, name='logs_auditorio'),
    path('detail_aditorio/<str:id>', detail_aditorio, name='detail_aditorio'),


]