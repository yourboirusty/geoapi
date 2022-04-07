from rest_framework import serializers


class WorkerStatusResponseSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)
    response = serializers.CharField(max_length=100, allow_blank=True)


# TODO: Add validation to check if loopup address is compliant
class AddressLookupSerializer(serializers.Serializer):
    lookup_address = serializers.CharField(max_length=100)


class AddressLookupResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=100)
