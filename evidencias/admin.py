from django.contrib import admin
from .models import Evidencia, TipoEvidencia, CadeiaCustomia, Arquivo

# Register your models here.

admin.site.register(Evidencia)
admin.site.register(TipoEvidencia)
admin.site.register(CadeiaCustomia)
admin.site.register(Arquivo)