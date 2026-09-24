from rest_framework.routers import DefaultRouter

from .views import ActivityViewSet

router = DefaultRouter()
router.register('atividades', ActivityViewSet, basename='atividade')

urlpatterns = router.urls
