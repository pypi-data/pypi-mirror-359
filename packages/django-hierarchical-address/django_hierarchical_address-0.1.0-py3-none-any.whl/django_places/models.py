from django.db import models

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
