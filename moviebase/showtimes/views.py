from .models import Cinema, Screening
from .serializers import CinemaSerializer, ScreeningSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django_filters import rest_framework as filters


class ScreeningsFilter(filters.FilterSet):
    movie = filters.CharFilter(field_name='movie__title', lookup_expr='icontains')
    city = filters.CharFilter(field_name='cinema__city', lookup_expr='icontains')

    class Meta:
        model = Screening
        fields = ['movie', 'city']


class CinemaListView(ListCreateAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


class CinemaView(RetrieveUpdateDestroyAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


class ScreeningListView(ListCreateAPIView):
    queryset = Screening.objects.all()
    serializer_class = ScreeningSerializer
    filterset_class = ScreeningsFilter


class ScreeningsView(RetrieveUpdateDestroyAPIView):
    queryset = Screening.objects.all()
    serializer_class = ScreeningSerializer
