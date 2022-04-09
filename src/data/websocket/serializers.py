from rest_framework import serializers


class WorkerStatusResponseSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=100)
    response = serializers.DictField(required=False)


class AddressLookupResponseSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=100)


class TaskLookupSerializer(serializers.Serializer):
    task_id = serializers.CharField(max_length=100)
