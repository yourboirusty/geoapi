from rest_framework import serializers
from data.models import GeoData
from validators import domain, ip_address


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


class AddressLookupSerializer(serializers.Serializer):
    lookup_address = serializers.CharField(max_length=100)

    def validate_lookup_address(self, value):
        if not (
            domain(value) or ip_address.ipv4(value) or ip_address.ipv6(value)
        ):
            raise serializers.ValidationError("Invalid lookup address")
        return value
