from django.urls import path
from .views import *


urlpatterns = [
    path('casos', caso, name='casos'),

    path('create_case/', create_case, name='create_case'),
    path('list_case/', list_case, name='list_case'),
    path('detail_case/<str:caso_id>/', detail_case, name='detail_case'),
    path('edit_case/<str:caso_id>/', edit_case, name='edit_case'),
    path('delete_case/<str:caso_id>/', delete_case, name='delete_case'),

    path('create_indiidual_involved/<str:caso_id>/', create_indiidual_involved, name='create_indiidual_involved'),
    path('list_indiidual_involved/', list_indiidual_involved, name='list_indiidual_involved'),
    path('detail_individual_invalid/<str:pessoa_id>/', detail_individual_invalid, name='detail_individual_invalid'),
    
    path('create_event/<str:caso_id>/', create_event, name='create_event'),
    path('list_event/', list_event, name='list_event'),
    path('detail_event/<str:id>/', detail_event, name='detail_event'),
    path('edit_event/<str:id>/', edit_event, name='edit_event'),
    path('delete_event/<str:id>/', delete_event, name='delete_event'),

    path('criminal_record/', criminal_record, name='criminal_record'),
]