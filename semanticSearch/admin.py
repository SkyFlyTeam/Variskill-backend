from django.contrib import admin

from .models import EntradaCorpus, PerguntaCorpus


class PerguntaCorpusInline(admin.TabularInline):
    # As formulações precisam de embedding: são editadas no JSON do corpus e sincronizadas com `seed_corpus`.
    model = PerguntaCorpus
    fields = ('texto',)
    readonly_fields = ('texto',)
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EntradaCorpus)
class EntradaCorpusAdmin(admin.ModelAdmin):
    list_display = ('pergunta', 'topico', 'ativo')
    list_filter = ('topico', 'ativo')
    search_fields = ('pergunta', 'resposta')
    inlines = (PerguntaCorpusInline,)
