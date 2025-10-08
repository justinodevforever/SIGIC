
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuario.urls')),
    path('', include('casos.urls')),
    path('', include('home.urls')),
    path('', include('authenticatio.urls')),
    path('', include('evidencias.urls')),
    path('', include('administrador.urls')),
]
