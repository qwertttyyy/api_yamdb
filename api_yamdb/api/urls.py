from api.views import UserViewSet, get_token, signup
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'users', UserViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', get_token),
    path('v1/auth/signup/', signup),
]
