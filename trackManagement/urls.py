from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MatriculaViewSet, PosicionarNivelView, RoadmapView, TrilhaViewSet

router = DefaultRouter()
router.register('trilhas', TrilhaViewSet, basename='trilha')
router.register('matriculas', MatriculaViewSet, basename='matricula')

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
