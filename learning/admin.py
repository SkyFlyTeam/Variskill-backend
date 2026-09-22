from django.contrib import admin

from activityManagement.models import Atividade, Conteudo
from questionsManagement.models import Questao, QuestaoOpcao

from .models import Module

admin.site.register(Module)
admin.site.register(Conteudo)
admin.site.register(Atividade)
admin.site.register(Questao)
admin.site.register(QuestaoOpcao)
