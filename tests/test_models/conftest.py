from pytest import fixture
from data.models import GeoData


@fixture
def geodata_dict(db, django_user_model):
    return {
        "user": django_user_model.objects.create(username="geodata_user"),
        "task_id": "1",
        "address": "127.0.0.1",
        "continent_name": "North America",
        "country_name": "United States",
        "region_name": "California",
        "city": "San Francisco",
        "latitude": "37.7749",
        "longitude": "-122.4194",
    }


@fixture
def geodata_object(db, geodata_dict):
    return GeoData.objects.create(**geodata_dict)
