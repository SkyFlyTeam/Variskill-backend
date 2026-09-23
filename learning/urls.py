from rest_framework.routers import DefaultRouter

from .views import ActivityViewSet, ContentViewSet

router = DefaultRouter()
router.register('atividades', ActivityViewSet, basename='atividade')
router.register('conteudos', ContentViewSet, basename='conteudo')

urlpatterns = router.urls
