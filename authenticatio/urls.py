from django.urls import path
from .views import *


urlpatterns = [
    path('accounts/login/', login_view, name='login'),
    path('logout/', logoutUser, name='logout'),
]
