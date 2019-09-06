from rest_framework import serializers
from .models import Cinema, Screening
from movielist.models import Movie


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = ('id', 'name', 'city')


class ScreeningSerializer(serializers.ModelSerializer):
    cinema = serializers.SlugRelatedField(slug_field='name', queryset=Cinema.objects.all())
    movie = serializers.SlugRelatedField(slug_field='title', queryset=Movie.objects.all())

    class Meta:
        model = Screening
        fields = ('id', 'cinema', 'movie', 'date')
