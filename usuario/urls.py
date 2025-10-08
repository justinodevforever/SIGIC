from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('reconhecimento/', views.index, name='index'),
    path('cadastrar/', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('verificar/', views.verificar_face, name='verificar_face'),
    path('listar/', views.listar_pessoas, name='listar_pessoas'),
    path('deletar/<int:pessoa_id>/', views.deletar_pessoa, name='deletar_pessoa'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

