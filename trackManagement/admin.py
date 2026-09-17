from django.contrib import admin
from .models import Trilha, Modulo, Matricula, ProgressoModulo


@admin.register(Trilha)
class TrilhaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'habilidade', 'ativo')
    search_fields = ('titulo', 'habilidade')


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'trilha', 'nivel', 'ordem_modulo')
    list_filter = ('nivel',)
    search_fields = ('titulo',)


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'trilha', 'status', 'criado_em')
    search_fields = ('usuario__nickName', 'trilha__titulo')


@admin.register(ProgressoModulo)
class ProgressoModuloAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'modulo', 'status', 'concluido_em')
    search_fields = ('matricula__usuario__nickName', 'modulo__titulo')
