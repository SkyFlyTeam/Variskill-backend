from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ConquistaListView,
    DiagnosticoPedagogicoView,
    EquiparItemView,
    EventoAuditoriaListView,
    InteresseListView,
    InventarioView,
    LoginView,
    LogoutView,
    RegisterView,
    SolicitacaoRevisaoViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('revisoes', SolicitacaoRevisaoViewSet, basename='revisao')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('interesses/', InteresseListView.as_view(), name='interesse-list'),
    path('auditoria/', EventoAuditoriaListView.as_view(), name='auditoria-list'),
    path('gamificacao/conquistas/', ConquistaListView.as_view(), name='gamificacao-conquistas'),
    path('gamificacao/inventario/', InventarioView.as_view(), name='gamificacao-inventario'),
    path(
        'gamificacao/inventario/<uuid:inventario_id>/equipar/',
        EquiparItemView.as_view(),
        name='gamificacao-inventario-equipar',
    ),
    # Antes do router: rota fixa sob users/me/, fora do UserViewSet (VAR-126).
    path(
        'users/me/diagnostico-pedagogico/',
        DiagnosticoPedagogicoView.as_view(),
        name='diagnostico-pedagogico',
    ),
    *router.urls,
]
