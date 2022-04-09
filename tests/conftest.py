from pytest import fixture
from data.models import GeoData
from data.tasks import process_geodata
from rest_framework.test import APIClient
from authentication.serializers import UserTokenObtainPairSerializer
from data.websocket.consumers import WorkerResponseConsumer
from data.websocket.utils import StackedAsyncJsonWebsocketConsumer
from unittest.mock import PropertyMock
from .utils import AsyncMock
from requests import Response


@fixture
def rest_client():
    return APIClient()


@fixture
def consumer():
    consumer = WorkerResponseConsumer()
    consumer.scope = PropertyMock()
    consumer.channel_layer = AsyncMock()
    consumer.channel_name = "CHANNEL1"
    return consumer


@fixture
def authorized_consumer(consumer):
    consumer.scope = {
        "user": {
            "id": 1,
            "slug": "USER1",
        }
    }
    return consumer


@fixture
def unauthorized_consumer(consumer):
    consumer.scope = {"user": None}
    return consumer


@fixture
def accept_consumer_mocker(mocker):
    return mocker.patch.object(StackedAsyncJsonWebsocketConsumer, "accept")


@fixture
def close_consumer_mocker(mocker):
    return mocker.patch.object(StackedAsyncJsonWebsocketConsumer, "close")


@fixture
def send_consumer_mocker(mocker):
    return mocker.patch.object(StackedAsyncJsonWebsocketConsumer, "_send")


@fixture
def geodata_result_mocker(mocker):
    return mocker.patch.object(process_geodata, "AsyncResult")


@fixture
def geodata_user(db, django_user_model):
    return django_user_model.objects.create(username="geodata_user")


@fixture
def geodata_user_token_pair(geodata_user):
    pair = UserTokenObtainPairSerializer.get_token(geodata_user)
    return str(pair), str(pair.access_token)


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
