from datetime import datetime

from rest_framework import serializers

from reviews.models import Titles, Genres, Categories


class TitleSerializer(serializers.ModelSerializer):
    description = serializers.CharField(required=False)
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genres.objects,
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Categories.objects
    )

    class Meta:
        model = Titles
        fields = '__all__'

    def validate(self, data):
        if data.get('genre') not in Genres.objects.values_list(
                'slug', flat=True
        ):
            raise serializers.ValidationError('Такого жанра нет в списке')
        if data.get('category') not in Categories.objects.values_list(
                'slug', flat=True
        ):
            raise serializers.ValidationError('Такой категории нет в списке')
        if data.get('year') > datetime.today().year:
            raise serializers.ValidationError('Это произведение ещё не вышло')

        return data
