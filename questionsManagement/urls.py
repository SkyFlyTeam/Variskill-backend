from rest_framework.routers import DefaultRouter

from .views import QuestaoViewSet

router = DefaultRouter()
router.register('questoes', QuestaoViewSet, basename='questao')

urlpatterns = router.urls
