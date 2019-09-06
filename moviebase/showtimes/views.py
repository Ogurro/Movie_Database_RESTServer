from .models import Cinema, Screening
from .serializers import CinemaSerializer, ScreeningSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


class CinemaListView(ListCreateAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


class CinemaView(RetrieveUpdateDestroyAPIView):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer


class ScreeningListView(ListCreateAPIView):
    queryset = Screening.objects.all()
    serializer_class = ScreeningSerializer


class ScreeningsView(RetrieveUpdateDestroyAPIView):
    queryset = Screening.objects.all()
    serializer_class = ScreeningSerializer
