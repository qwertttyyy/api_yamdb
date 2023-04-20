from django_filters import FilterSet

from reviews.models import Titles


class TitlesFilter(FilterSet):
    class Meta:
        model = Titles
        fields = [
            'category__slug',
            'genre__slug',
            'name',
            'year',
        ]
