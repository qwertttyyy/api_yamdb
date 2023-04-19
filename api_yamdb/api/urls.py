from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TitleViewSet


router_v1 = DefaultRouter()

router_v1.register(r'titles', TitleViewSet)

v1 = [
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('v1/', include(v1)),
]
