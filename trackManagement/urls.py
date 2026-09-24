from django.urls import path
from .views import RoadmapView
urlpatterns = [path('trilhas/<uuid:trilha_id>/roadmap/', RoadmapView.as_view(), name='trilha-roadmap')]
