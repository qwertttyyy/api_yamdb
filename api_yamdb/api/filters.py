from django_filters import FilterSet

from reviews.models import Title


class TitlesFilter(FilterSet):
    class Meta:
        model = Title
        fields = [
            'category__slug',
            'genre__slug',
            'name',
            'year',
        ]
