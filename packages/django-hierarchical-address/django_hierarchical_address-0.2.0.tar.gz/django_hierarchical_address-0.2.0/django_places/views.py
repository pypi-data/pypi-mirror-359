from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .models import Continent, Country, StateProvince, City, County, Address
from .serializers import (
    ContinentSerializer, CountrySerializer, StateProvinceSerializer,
    CitySerializer, CountySerializer, AddressSerializer
)

# Create your views here.

class ContinentViewSet(viewsets.ModelViewSet):
    queryset = Continent.objects.all()  # type: ignore[attr-defined]
    serializer_class = ContinentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code']

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()  # type: ignore[attr-defined]
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'continent']

class StateProvinceViewSet(viewsets.ModelViewSet):
    queryset = StateProvince.objects.all()  # type: ignore[attr-defined]
    serializer_class = StateProvinceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'code', 'country']

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()  # type: ignore[attr-defined]
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'state_province']

class CountyViewSet(viewsets.ModelViewSet):
    queryset = County.objects.all()  # type: ignore[attr-defined]
    serializer_class = CountySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'city']

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()  # type: ignore[attr-defined]
    serializer_class = AddressSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['continent', 'country', 'state_province', 'city', 'county', 'zip_code']
