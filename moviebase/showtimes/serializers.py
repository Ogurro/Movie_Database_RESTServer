from rest_framework import serializers
from .models import Cinema, Screening
from movielist.models import Movie


class CinemaMovieListSerializer(serializers.ModelSerializer):
    movie_id = serializers.ReadOnlyField(source='movie.id')
    movie_title = serializers.ReadOnlyField(source='movie.title')

    class Meta:
        model = Screening
        fields = ('movie_id', 'movie_title',)


class CinemaSerializer(serializers.ModelSerializer):
    movies = CinemaMovieListSerializer(source='screening_set', many=True, read_only=True)

    class Meta:
        model = Cinema
        fields = ('id', 'name', 'city', 'movies')


class ScreeningSerializer(serializers.ModelSerializer):
    cinema = serializers.SlugRelatedField(slug_field='name', queryset=Cinema.objects.all())
    movie = serializers.SlugRelatedField(slug_field='title', queryset=Movie.objects.all())

    class Meta:
        model = Screening
        fields = ('id', 'cinema', 'movie', 'date')
