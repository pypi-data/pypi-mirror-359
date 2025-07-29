from django.contrib import admin
from .models import Continent, Country, StateProvince, City, County, Address
from django import forms

class AddressAdminForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        country = self.initial.get('country') or (self.instance.country if self.instance else None)
        state_province = self.initial.get('state_province') or (self.instance.state_province if self.instance else None)
        city = self.initial.get('city') or (self.instance.city if self.instance else None)
        # Filter state_province by country
        if country:
            self.fields['state_province'].queryset = StateProvince.objects.filter(country=country)
        else:
            self.fields['state_province'].queryset = StateProvince.objects.none()
        # Filter city by state_province
        if state_province:
            self.fields['city'].queryset = City.objects.filter(state_province=state_province)
        else:
            self.fields['city'].queryset = City.objects.none()
        # Filter county by city
        if city:
            self.fields['county'].queryset = County.objects.filter(city=city)
        else:
            self.fields['county'].queryset = County.objects.none()

class AddressAdmin(admin.ModelAdmin):
    form = AddressAdminForm
    class Media:
        js = ('django_places/address_chained.js',)

admin.site.register(Continent)
admin.site.register(Country)
admin.site.register(StateProvince)
admin.site.register(City)
admin.site.register(County)
admin.site.register(Address, AddressAdmin)
