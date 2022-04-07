from pytest import fixture
from data.models import GeoData
from rest_framework.test import APIClient
from requests import Response


@fixture
def rest_client():
    return APIClient()


@fixture
def geodata_user(db, django_user_model):
    return django_user_model.objects.create(username="geodata_user")


@fixture
def geodata_dict(db, geodata_user):
    return {
        "user": geodata_user,
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


@fixture
def good_response():
    response = Response()
    response.status_code = 200
    return response


@fixture
def good_ipstack_response(good_response):
    good_response.json = lambda: {
        "continent_name": "North America",
        "country_name": "United States",
        "region_name": "California",
        "city": "San Francisco",
        "latitude": "37.7749",
        "longitude": "-122.4194",
    }

    return good_response
