# Django Hierarchical Address

A reusable Django app for hierarchical, international address fields with full REST API and Django admin support. Easily add continent, country, state/province, city, county, and detailed address fields to any model, with automatic filtering and dynamic dropdowns.

---

## Features
- Hierarchical address models: Continent, Country, State/Province, City, County, Address
- International standards (ISO codes, etc.)
- Full Django REST Framework API with filtering and nested serialization
- Django admin integration with dynamic, chained selects (custom JavaScript)
- Highly customizable and extensible
- Use as relations (ForeignKey/OneToOne) or as embedded models/fields
- Ready for pip installation

---

## Installation

1. **Install the package (in your Django project):**
   ```bash
   pip install django-hierarchical-address
   # OR for local development:
   pip install -e /path/to/your/django-hierarchical-address
   ```

2. **Add to `INSTALLED_APPS` in your `settings.py`:**
   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'django_filters',
       'django_places',
   ]
   ```

3. **Include the API URLs in your main `urls.py`:**
   ```python
   from django.urls import path, include

   urlpatterns = [
       # ...
       path('api/places/', include('django_places.urls')),
   ]
   ```

4. **(Optional, for admin dynamic selects) Ensure static files are collected:**
   ```bash
   python manage.py collectstatic
   ```

---

## Usage

### 1. **Migrate the database:**
   ```bash
   python manage.py makemigrations django_places
   python manage.py migrate
   ```

### 2. **Register address fields in your models:**

You can use the provided `Address` model as a ForeignKey or OneToOneField in your own models:

```python
from django.db import models
from django_places.models import Address

class MyModel(models.Model):
    name = models.CharField(max_length=100)
    address = models.OneToOneField(Address, on_delete=models.CASCADE)
```

### 3. **Use as Embedded Models/Fields or Custom Fields**

You can now use the address models as embedded fields (not just relations) using custom fields. For example:

```python
from django.db import models
from django_places.models import CountryField, StateProvinceField, CityField, CountyField

class MyCustomAddress(models.Model):
    country = CountryField(null=True, blank=True, help_text="Country of origin")
    state_province = StateProvinceField(null=True, blank=True)
    city = CityField(null=True, blank=True)
    county = CountyField(null=True, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    # ... add your own fields ...
```

All standard Django field options (`null`, `blank`, `default`, `help_text`, etc.) are supported for these custom fields.

Or, you can use the provided models as abstract base classes to create your own address model:

```python
from django_places.models import Address

class MyAbstractAddress(Address):
    extra_field = models.CharField(max_length=100)
    class Meta:
        abstract = True
```

### 4. **Django Admin**
- All address models are registered in the admin.
- The Address admin form features dynamic dropdowns for country, state/province, city, and county.
- When you select a parent (e.g., country), the child dropdown (e.g., state/province) updates instantly.

**Admin Form Example:**
![Admin Form Example](docs/admin_form_example.png)

### 5. **REST API**
- All address models are available via REST endpoints:
  - `/api/places/continents/`
  - `/api/places/countries/`
  - `/api/places/states-provinces/`
  - `/api/places/cities/`
  - `/api/places/counties/`
  - `/api/places/addresses/`
- Filtering is supported via query parameters, e.g.:
  - `/api/places/countries/?continent=1`
  - `/api/places/states-provinces/?country=1`
  - `/api/places/cities/?state_province=1`
  - `/api/places/counties/?city=1`
- Nested serialization: Each object includes its parent objects for easy data consumption.
- When creating/updating an Address, only valid child options are accepted (e.g., only cities in the selected state).

**API Example: Create Address**
```json
POST /api/places/addresses/
{
  "continent_id": 1,
  "country_id": 2,
  "state_province_id": 5,
  "city_id": 10,
  "county_id": 20,
  "address_line": "123 Main St",
  "zip_code": "12345",
  "location": "51.5074,-0.1278",
  "details": "Near the park"
}
```

**API Example: Get Address**
```json
{
  "id": 1,
  "continent": {"id": 1, "name": "Europe", "code": "EU"},
  "country": {"id": 2, "name": "United Kingdom", "code": "GBR", "continent": 1},
  "state_province": {"id": 5, "name": "England", "code": "ENG", "country": 2},
  "city": {"id": 10, "name": "London", "state_province": 5},
  "county": {"id": 20, "name": "Camden", "city": 10},
  "address_line": "123 Main St",
  "zip_code": "12345",
  "location": "51.5074,-0.1278",
  "details": "Near the park"
}
```

**API Example: Filter Cities by State/Province**
```http
GET /api/places/cities/?state_province=5
```

---

## Customization

- **Extend models:** You can subclass or swap out any model for your own needs.
- **Override serializers or viewsets:** For custom API behavior, override the provided serializers or viewsets in your project.
- **Admin customization:** The admin form uses custom JavaScript for chained selects. You can further customize this by editing `django_places/static/django_places/address_chained.js`.
- **Use as fields or embedded models:** You can use the address models as fields in your own models, or as abstract base classes.
- **Custom field options:** All custom address fields accept standard Django field options (`null`, `blank`, `default`, `help_text`, etc.).

---

## Requirements
- Django >= 3.2
- djangorestframework
- django-filter

---

## Development & Testing

1. Clone the repo and install in editable mode:
   ```bash
   git clone https://github.com/ashkanhasani/django-hierarchical-address.git
   cd django-hierarchical-address
   pip install -e .
   ```
2. Run the example project:
   ```bash
   cd example_project
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
3. Access the admin at `http://127.0.0.1:8000/admin/` and the API at `http://127.0.0.1:8000/api/places/`

---

## FAQ

**Q: Can I use my own models for Country, City, etc.?**
A: Yes! You can subclass or swap out any model. Just ensure you maintain the foreign key relationships.

**Q: How do I add more fields to Address?**
A: Subclass the Address model and add your fields, or use a OneToOneField to extend it.

**Q: Can I use this in a multi-tenant or multi-language project?**
A: Yes, the models are designed to be extensible. For multi-language, consider using [django-parler](https://django-parler.readthedocs.io/) or similar.

**Q: Can I use address models as fields instead of relations?**
A: Yes! You can use the address models as fields in your own models, or as abstract base classes for embedded address data. All standard Django field options are supported for these fields.

---

## License
MIT

---

## Contributing
Pull requests and issues are welcome! Please see the repo for guidelines.

---

## Credits
- [Django REST Framework](https://www.django-rest-framework.org/)
- [django-filter](https://django-filter.readthedocs.io/)
- Inspired by real-world address needs and open data standards.
