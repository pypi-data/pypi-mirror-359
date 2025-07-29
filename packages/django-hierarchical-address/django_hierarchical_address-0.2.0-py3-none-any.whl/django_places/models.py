from django.db import models
import json

# Create your models here.

class Continent(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, help_text="Standard continent code (e.g., EU, NA)")

    class Meta:
        verbose_name = "Continent"
        verbose_name_plural = "Continents"

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True, help_text="ISO 3166-1 alpha-3 code")
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name="countries")

    class Meta:
        verbose_name = "Country"
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name

class StateProvince(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, help_text="State/Province code")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states_provinces")

    class Meta:
        verbose_name = "State/Province"
        verbose_name_plural = "States/Provinces"

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=100)
    state_province = models.ForeignKey(StateProvince, on_delete=models.CASCADE, related_name="cities")

    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name

class County(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="counties")

    class Meta:
        verbose_name = "County"
        verbose_name_plural = "Counties"

    def __str__(self):
        return self.name

class Address(models.Model):
    continent = models.ForeignKey(Continent, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    state_province = models.ForeignKey(StateProvince, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True, help_text="Optional: latitude,longitude or point field")
    details = models.TextField(blank=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        parts = [self.address_line, self.city.name if self.city else '', self.state_province.name if self.state_province else '', self.country.name if self.country else '']
        return ", ".join([p for p in parts if p])

class ContinentField(models.JSONField):
    description = "A field to store continent data as JSON"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        data = super().from_db_value(value, expression, connection)
        from .models import Continent
        return Continent(**data) if data else None
    def to_python(self, value):
        from .models import Continent
        if isinstance(value, Continent) or value is None:
            return value
        if isinstance(value, dict):
            return Continent(**value)
        if isinstance(value, str):
            return Continent(**json.loads(value))
        return value
    def get_prep_value(self, value):
        if hasattr(value, '__dict__'):
            return {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
        return value

class CountryField(models.JSONField):
    description = "A field to store country data as JSON"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        data = super().from_db_value(value, expression, connection)
        from .models import Country
        return Country(**data) if data else None
    def to_python(self, value):
        from .models import Country
        if isinstance(value, Country) or value is None:
            return value
        if isinstance(value, dict):
            return Country(**value)
        if isinstance(value, str):
            return Country(**json.loads(value))
        return value
    def get_prep_value(self, value):
        if hasattr(value, '__dict__'):
            return {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
        return value

class StateProvinceField(models.JSONField):
    description = "A field to store state/province data as JSON"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        data = super().from_db_value(value, expression, connection)
        from .models import StateProvince
        return StateProvince(**data) if data else None
    def to_python(self, value):
        from .models import StateProvince
        if isinstance(value, StateProvince) or value is None:
            return value
        if isinstance(value, dict):
            return StateProvince(**value)
        if isinstance(value, str):
            return StateProvince(**json.loads(value))
        return value
    def get_prep_value(self, value):
        if hasattr(value, '__dict__'):
            return {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
        return value

class CityField(models.JSONField):
    description = "A field to store city data as JSON"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        data = super().from_db_value(value, expression, connection)
        from .models import City
        return City(**data) if data else None
    def to_python(self, value):
        from .models import City
        if isinstance(value, City) or value is None:
            return value
        if isinstance(value, dict):
            return City(**value)
        if isinstance(value, str):
            return City(**json.loads(value))
        return value
    def get_prep_value(self, value):
        if hasattr(value, '__dict__'):
            return {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
        return value

class CountyField(models.JSONField):
    description = "A field to store county data as JSON"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        data = super().from_db_value(value, expression, connection)
        from .models import County
        return County(**data) if data else None
    def to_python(self, value):
        from .models import County
        if isinstance(value, County) or value is None:
            return value
        if isinstance(value, dict):
            return County(**value)
        if isinstance(value, str):
            return County(**json.loads(value))
        return value
    def get_prep_value(self, value):
        if hasattr(value, '__dict__'):
            return {k: v for k, v in value.__dict__.items() if not k.startswith('_')}
        return value
