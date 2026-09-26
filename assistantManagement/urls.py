from django.urls import path
from assistantManagement.views import DecidirNivelView

app_name = 'assistantManagement'

urlpatterns = [
    path(
        'sessao/<uuid:sessao_id>/decidir-nivel/',
        DecidirNivelView.as_view(),
        name='decidir-nivel',
    ),
]

