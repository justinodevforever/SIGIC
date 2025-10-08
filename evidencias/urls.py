from django.urls import path
from .views import *


urlpatterns = [
    path('create_evidence/<str:caso_id>/', create_evidence, name='create_evidence'),
    path('list_evidence/', list_evidence, name='list_evidence'),
    path('detail_evidence/<str:id>/', detail_evidence, name='detail_evidence'),
    path('edit_evidence/<str:id>/', edit_evidence, name='edit_evidence'),
    path('delete_evidence/<str:id>/', delete_evidence, name='delete_evidence'),
    path('moviment_evidence/<str:id>/', moviment_evidence, name='moviment_evidence'),

    path('get_evidence/', get_evidence, name='get_evidence'),

    path('create_expertise/', create_expertise, name='create_expertise'),
    path('list_evidence_expertise/', list_evidence_expertise, name='list_evidence_expertise'),
    path('detail_expertise/<str:id>/', detail_expertise, name='detail_expertise'),
    path('edit_expertise/<str:id>/', edit_expertise, name='edit_expertise'),
    path('delete_expertise/<str:id>/', delete_expertise, name='delete_expertise'),
]
