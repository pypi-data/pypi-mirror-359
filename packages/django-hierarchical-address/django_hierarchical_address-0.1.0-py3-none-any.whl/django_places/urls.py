from rest_framework.routers import DefaultRouter
from .views import (
    ContinentViewSet, CountryViewSet, StateProvinceViewSet,
    CityViewSet, CountyViewSet, AddressViewSet
)

router = DefaultRouter()
router.register(r'continents', ContinentViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'states-provinces', StateProvinceViewSet)
router.register(r'cities', CityViewSet)
router.register(r'counties', CountyViewSet)
router.register(r'addresses', AddressViewSet)

urlpatterns = router.urls
