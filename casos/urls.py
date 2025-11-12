from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('casos', caso, name='casos'),

    path('create_case/', create_case, name='create_case'),
    path('list_case/', list_case, name='list_case'),
    path('detail_case/<str:caso_id>/', detail_case, name='detail_case'),
    path('edit_case/<str:caso_id>/', edit_case, name='edit_case'),
    path('delete_case/<str:caso_id>/', delete_case, name='delete_case'),

    path('create_individual_involved/<str:caso_id>/', create_individual_involved, name='create_individual_involved'),
    path('list_individual_involved/', list_individual_involved, name='list_individual_involved'),
    path('detail_individual_invalid/<str:pessoa_id>/', detail_individual_invalid, name='detail_individual_invalid'),
    path('delete_individual_involved/<str:id>/', delete_individual_involved, name='delete_individual_involved'),
    path('edit_individual_involved/<str:id>/', edit_individual_involved, name='edit_individual_involved'),
    
    path('create_event/<str:caso_id>/', create_event, name='create_event'),
    path('list_event/', list_event, name='list_event'),
    path('detail_event/<str:id>/', detail_event, name='detail_event'),
    path('edit_event/<str:id>/', edit_event, name='edit_event'),
    path('delete_event/<str:id>/', delete_event, name='delete_event'),

    path('criminal_record/', criminal_record, name='criminal_record'),

    path('list_suspect/', list_suspect, name='list_suspect'),
    path('detail_suspect/<str:id>/', detail_suspect, name='detail_suspect'),

    path('create_type_crime/', create_type_crime, name='create_type_crime'),
    path('list_type_crime/', list_type_crime, name='list_type_crime'),
    path('delete_typr_crime/<str:id>/', delete_typr_crime, name='delete_typr_crime'),
    path('edit_type_crime/<str:id>/', edit_type_crime, name='edit_type_crime'),
    path('datail_type_crime/<str:id>/', datail_type_crime, name='datail_type_crime'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)