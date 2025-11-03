from django.urls import path
from .views import *

urlpatterns = [
  path('', dashboard, name='home' ),
  path('perfil/', perfil, name='perfil' )
]
