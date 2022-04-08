import pytest
from data.models import GeoData, GeoDataSlugEnded


def test_slug_generation(db, django_user_model, django_assert_num_queries):
    user = django_user_model.objects.create(username="geodata_user")
    with django_assert_num_queries(2):
        geodata_object = GeoData.objects.create(
            user=user,
            task_id="1",
            address="127.0.0.1",
            continent_name="North America",
            country_name="United States",
            region_name="California",
            city="San Francisco",
            latitude="37.7749",
            longitude="-122.4194",
        )
    assert geodata_object.slug


def test_slug_generation_with_multiple_saves(
    db, django_user_model, django_assert_num_queries, geodata_object
):
    slug = geodata_object.slug
    geodata_object.task_id = "2"
    with django_assert_num_queries(1):
        geodata_object.save()

    assert geodata_object.slug == slug


def test_slug_duplicate_regeneration(mocker, db, geodata_object, geodata_dict):
    slug = geodata_object.slug

    m = mocker.patch("data.models.get_random_string", return_value=slug)
    with pytest.raises(GeoDataSlugEnded):
        new_geodata_object = GeoData.objects.create(**geodata_dict)
