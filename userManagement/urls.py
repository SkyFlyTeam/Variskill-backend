from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import LoginView, RegisterView, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    *router.urls,
]
