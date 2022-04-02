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


class WorkerStatusResponseSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=100, required=False)


class AddressLookupSerializer(serializers.Serializer):
    lookup_address = serializers.CharField(max_length=100)


class AddressLookupResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=100)
