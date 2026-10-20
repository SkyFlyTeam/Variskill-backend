from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ConsentimentoDetailView,
    ConsentimentoListView,
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
    path('consentimentos/', ConsentimentoListView.as_view(), name='consentimento-list'),
    path(
        'consentimentos/<str:tipo>/',
        ConsentimentoDetailView.as_view(),
        name='consentimento-detail',
    ),
    *router.urls,
]
