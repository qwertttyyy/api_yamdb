from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
    get_token,
    signup,
)

router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review',
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)

router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', get_token),
    path('v1/auth/signup/', signup),
]
