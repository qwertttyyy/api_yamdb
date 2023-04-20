from api.views import (CommentViewSet, ReviewViewSet, UserViewSet, get_token,
                       signup)
from django.urls import include, path
from rest_framework.routers import DefaultRouter

router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', get_token),
    path('v1/auth/signup/', signup),
]
