from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PosicionarNivelView, RoadmapView

router = DefaultRouter()

urlpatterns = [
    path(
        'trilhas/<uuid:trilha_id>/roadmap/',
        RoadmapView.as_view(),
        name='trilha-roadmap',
    ),
    path(
        'diagnostico/<uuid:atividade_id>/posicionar-nivel/',
        PosicionarNivelView.as_view(),
        name='diagnostico-posicionar-nivel',
    ),
] + router.urls
