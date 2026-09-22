from rest_framework.routers import DefaultRouter

from .views import ActivityViewSet, ContentViewSet, ModuleViewSet

router = DefaultRouter()
router.register('modulos', ModuleViewSet, basename='modulo')
router.register('atividades', ActivityViewSet, basename='atividade')
router.register('conteudos', ContentViewSet, basename='conteudo')

urlpatterns = router.urls
