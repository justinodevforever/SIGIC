from django.contrib import admin
from .models import Usuario, Pessoa, ConfiguracaoSistema, LogAuditoria, Endereco, AliasPessoa,PessoaReconhecimento,HistoricoReconhecimento


# Register your models here.

admin.site.register(Usuario)
admin.site.register(Pessoa)
admin.site.register(Endereco)
admin.site.register(AliasPessoa)
admin.site.register(ConfiguracaoSistema)
admin.site.register(LogAuditoria)
admin.site.register(PessoaReconhecimento)
admin.site.register(HistoricoReconhecimento)