from django.urls import path
from .views import *
from casos.views import *

urlpatterns = [
    path('create_user/', create_user, name='create_user'),
    path('list_user/', list_user, name='list_user'),
    path('edit_user/<int:id>/', edit_user, name='edit_user'),
    path('view_user/<int:id>/', view_user, name='view_user'),
    path('delete_user/<int:id>/', delete_user, name='delete_user'),
    path('exe/', exe, name='exe'),
]
