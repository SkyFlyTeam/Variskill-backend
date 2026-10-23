from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    EventoAuditoriaListView,
    InteresseListView,
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
    *router.urls,
]
