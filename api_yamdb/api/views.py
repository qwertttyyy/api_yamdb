from rest_framework import viewsets

from api.filters import TitlesFilter
from api.permissions import IsAdminOrReadOnly
from api.serializers import TitleSerializer
from reviews.models import Titles


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_class = TitlesFilter
