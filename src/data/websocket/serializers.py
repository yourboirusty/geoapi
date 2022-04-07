from rest_framework import serializers
from validators import domain, ip_address


class WorkerStatusResponseSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)
    response = serializers.CharField(max_length=100, allow_blank=True)


class AddressLookupSerializer(serializers.Serializer):
    lookup_address = serializers.CharField(max_length=100)

    def validate_lookup_address(self, value):
        if not (
            domain(value) or ip_address.ipv4(value) or ip_address.ipv6(value)
        ):
            raise serializers.ValidationError("Invalid lookup address")
        return value


class AddressLookupResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=100)
