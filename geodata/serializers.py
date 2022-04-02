from rest_framework import serializers
from geodata.models import GeoData


class GeoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeoData
        fields = (
            "slug",
            "timestamp",
            "address",
            "continent_name",
            "country_name",
            "region_name",
            "city",
            "latitude",
            "longitude",
        )

        read_only_fields = ("slug", "timestamp", "address")

        lookup_field = "slug"
