import pytest
from unittest.mock import call
from data.tasks import process_geodata
from data.models import GeoData


@pytest.mark.parametrize(
    "input_address",
    ["192.168.1.1", "google.com", "2001:0db8:85a3:0000:0000:8a2e:0370:7334"],
)
def test_process_geodata(
    mocker,
    celery_session_app,
    celery_session_worker,
    geodata_user,
    worker_sender_mocker,
    ipstack_request_mock,
    input_address,
    ipstack_dict,
):
    geodata_write_mock = mocker.patch("data.models.GeoData.objects.create")
    task = process_geodata.delay(input_address, "USER1")  # type: ignore
    geodata_slug = task.get()
    data = {
        "continent_name": "North America",
        "country_name": "United States",
        "region_name": "California",
        "city": "Los Angeles",
        "latitude": "34.0453",
        "longitude": "-118.2413",
    }
    assert geodata_slug is not None
    assert geodata_write_mock.called
    assert geodata_write_mock.call_count == 1
    assert geodata_write_mock.mock_calls[0] == call(
        user=geodata_user, address=input_address, **data
    )
    # assert worker_sender_mocker.call_count > 0
