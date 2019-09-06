from .models import Movie
from .serializers import MovieSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class MovieListView(ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieView(RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
