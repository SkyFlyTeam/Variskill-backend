from rest_framework.routers import DefaultRouter

from .views import ModuloViewSet

router = DefaultRouter()
router.register('modulos', ModuloViewSet, basename='modulo')

urlpatterns = router.urls
