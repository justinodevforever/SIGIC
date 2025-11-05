from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('reconhecimento/', index, name='index'),
    path('cadastrar/', cadastrar_pessoa, name='cadastrar_pessoa'),
    path('verificar/', verificar_face, name='verificar_face'),
    path('listar/', listar_pessoas, name='listar_pessoas'),
    path('deletar/<int:pessoa_id>/', deletar_pessoa, name='deletar_pessoa'),

     path('create_user/', create_user, name='create_user'),
    path('list_user/', list_user, name='list_user'),
    path('edit_user/<str:id>/', edit_user, name='edit_user'),
    path('view_user/<str:id>/', view_user, name='view_user'),
    path('delete_user/<str:id>/', delete_user, name='delete_user'),
    
    path('dateil_researcher/<str:id>/', dateil_researcher, name='dateil_researcher'),
    path('list_researcher/', list_researcher, name='list_researcher'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

