from django.contrib import admin
from .models import Caso, Comentario, EnvolvimentoCaso, EventoTimeline, TipoCrime

admin.site.register(Caso)
admin.site.register(Comentario)
admin.site.register(EnvolvimentoCaso)
admin.site.register(EventoTimeline)
admin.site.register(TipoCrime)