import pytest
from django.urls import reverse
from data.serializers import AddressLookupSerializer


@pytest.mark.parametrize(
    "url_name,kwargs",
    [("geodata-list", None), ("geodata-detail", {"slug": "aaaaa"})],
)
def test_unauthorized_on_anon(rest_client, geodata_user, url_name, kwargs):
    response = rest_client.get(
        reverse(
            url_name,
            kwargs=kwargs,
        ),
    )
    assert response.status_code == 401
    rest_client.force_authenticate(user=geodata_user)
    response = rest_client.get(reverse(url_name, kwargs=kwargs))
    assert response.status_code != 401


@pytest.mark.parametrize(
    "address,expected_response",
    [
        ("", False),
        ("a", False),
        ("a.b.c.d", False),
        ("google.com", True),
        ("192.168.1.1", True),
        ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", True),
    ],
)
def test_lookup_address_validation(
    rest_client,
    geodata_user,
    address,
    expected_response,
):
    serializer = AddressLookupSerializer(data={"lookup_address": address})
    assert serializer.is_valid() == expected_response
