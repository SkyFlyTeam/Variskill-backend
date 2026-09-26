from django.urls import path
from assistantManagement.views import (
    DecidirNivelView,
    EnviarMensagemView,
    HistoricoSessaoView,
    IniciarSessaoView,
)

app_name = 'assistantManagement'

urlpatterns = [
    path(
        'sessao/iniciar/',
        IniciarSessaoView.as_view(),
        name='iniciar-sessao',
    ),
    path(
        'sessao/<uuid:sessao_id>/mensagem/',
        EnviarMensagemView.as_view(),
        name='enviar-mensagem',
    ),
    path(
        'sessao/<uuid:sessao_id>/historico/',
        HistoricoSessaoView.as_view(),
        name='historico-sessao',
    ),
    path(
        'sessao/<uuid:sessao_id>/decidir-nivel/',
        DecidirNivelView.as_view(),
        name='decidir-nivel',
    ),
]


