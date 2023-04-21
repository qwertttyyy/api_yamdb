from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc',
    ),
    path(
        'doc/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swager-ui',
    ),
]
