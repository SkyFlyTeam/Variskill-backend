"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

@method_decorator(ensure_csrf_cookie, name='dispatch')
class SwaggerView(SpectacularSwaggerView):
    template_name_js = 'swagger_ui_csrf.js'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        response["X-CSRFToken"] = get_token(request)
        return response

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('userManagement.urls')),
    path('api/', include('learning.urls')),
    path('api/', include('trackManagement.urls')),
    path('api/', include('questionsManagement.urls')),
    path('api/chat/', include('assistantManagement.urls')),
    path('api/auth/', include('rest_framework.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
]
