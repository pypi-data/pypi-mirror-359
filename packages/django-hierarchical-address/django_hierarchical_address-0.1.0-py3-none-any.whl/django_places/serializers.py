from rest_framework import serializers
from .models import Continent, Country, StateProvince, City, County, Address

class ContinentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Continent
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    continent = ContinentSerializer(read_only=True)
    continent_id = serializers.PrimaryKeyRelatedField(
        queryset=Continent.objects.all(), source='continent', write_only=True
    )
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'continent', 'continent_id']

class StateProvinceSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source='country', write_only=True
    )
    class Meta:
        model = StateProvince
        fields = ['id', 'name', 'code', 'country', 'country_id']

class CitySerializer(serializers.ModelSerializer):
    state_province = StateProvinceSerializer(read_only=True)
    state_province_id = serializers.PrimaryKeyRelatedField(
        queryset=StateProvince.objects.all(), source='state_province', write_only=True
    )
    class Meta:
        model = City
        fields = ['id', 'name', 'state_province', 'state_province_id']

class CountySerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(), source='city', write_only=True
    )
    class Meta:
        model = County
        fields = ['id', 'name', 'city', 'city_id']

class AddressSerializer(serializers.ModelSerializer):
    continent = ContinentSerializer(read_only=True)
    continent_id = serializers.PrimaryKeyRelatedField(
        queryset=Continent.objects.all(), source='continent', write_only=True, required=False
    )
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), source='country', write_only=True, required=False
    )
    state_province = StateProvinceSerializer(read_only=True)
    state_province_id = serializers.PrimaryKeyRelatedField(
        queryset=StateProvince.objects.none(), source='state_province', write_only=True, required=False
    )
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.none(), source='city', write_only=True, required=False
    )
    county = CountySerializer(read_only=True)
    county_id = serializers.PrimaryKeyRelatedField(
        queryset=County.objects.none(), source='county', write_only=True, required=False
    )
    class Meta:
        model = Address
        fields = [
            'id', 'continent', 'continent_id', 'country', 'country_id',
            'state_province', 'state_province_id', 'city', 'city_id',
            'county', 'county_id', 'address_line', 'zip_code', 'location', 'details'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        country_id = None
        state_province_id = None
        city_id = None
        # Try to get country from initial data (POST/PUT)
        if 'country_id' in self.initial_data:
            country_id = self.initial_data['country_id']
        elif self.instance and getattr(self.instance, 'country_id', None):
            country_id = self.instance.country_id
        if 'state_province_id' in self.initial_data:
            state_province_id = self.initial_data['state_province_id']
        elif self.instance and getattr(self.instance, 'state_province_id', None):
            state_province_id = self.instance.state_province_id
        if 'city_id' in self.initial_data:
            city_id = self.initial_data['city_id']
        elif self.instance and getattr(self.instance, 'city_id', None):
            city_id = self.instance.city_id
        # Filter state_province by country
        if country_id:
            self.fields['state_province_id'].queryset = StateProvince.objects.filter(country_id=country_id)
        else:
            self.fields['state_province_id'].queryset = StateProvince.objects.none()
        # Filter city by state_province
        if state_province_id:
            self.fields['city_id'].queryset = City.objects.filter(state_province_id=state_province_id)
        else:
            self.fields['city_id'].queryset = City.objects.none()
        # Filter county by city
        if city_id:
            self.fields['county_id'].queryset = County.objects.filter(city_id=city_id)
        else:
            self.fields['county_id'].queryset = County.objects.none()
