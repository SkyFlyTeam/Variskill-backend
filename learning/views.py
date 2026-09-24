from rest_framework import permissions, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from .models import Activity, Content
from .permissions import IsAdminForUnsafeMethods
from .serializers import ActivityCreateSerializer, ActivitySerializer, ContentSerializer


class ActivityViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminForUnsafeMethods)
    queryset = Activity.objects.select_related('content').prefetch_related('questions__options')

    def get_serializer_class(self):
        if self.action == 'create':
            return ActivityCreateSerializer
        return ActivitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ('list', 'retrieve') and not self.request.user.is_staff:
            queryset = queryset.filter(active=True)
        return queryset

    def destroy(self, request, *args, **kwargs):
        activity = self.get_object()
        activity.active = False
        activity.save(update_fields=['active'])
        return Response({'mensagem': 'Atividade desativada com sucesso.'})


class ContentViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsAdminForUnsafeMethods)
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
