from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response

from .serializers import AuthSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.all().order_by('id')


class RegisterView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['nickName'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            return Response(
                {'detail': 'Invalid credentials.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return Response(UserSerializer(user).data)
