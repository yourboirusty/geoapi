from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from data.models import GeoData
from geoapi.celery import app
from data.websocket.serializers import WorkerStatusResponseSerializer
from data.serializers import (
    GeoDataSerializer,
    AddressLookupSerializer,
)
import kombu.exceptions
from data.websocket.serializers import AddressLookupResponseSerializer
from data.tasks import process_geodata


class GeoDataViewSet(viewsets.ModelViewSet):
    serializer_class = GeoDataSerializer
    permission_classes = (IsAuthenticated,)
    allowed_methods = ("GET", "POST", "PUT", "DELETE")  # type: ignore
    lookup_field = "slug"
    filterset_fields = (
        "address",
        "continent_name",
        "country_name",
        "region_name",
        "city",
        "latitude",
        "longitude",
        "task_id",
        "timestamp",
    )

    def get_queryset(self):
        return GeoData.objects.filter(user=self.request.user)

    @extend_schema(
        request=AddressLookupSerializer,
        responses={200: AddressLookupResponseSerializer},
    )
    @action(methods=["post"], detail=False)
    def lookup(self, request: Request, *args, **kwargs):
        serializer = AddressLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = serializer.validated_data["lookup_address"]  # type: ignore
        try:
            task_id = app.send_task(
                "geoapi.tasks.process_geodata", (address, request.user.slug)
            )
        except kombu.exceptions.OperationalError:
            return Response(
                {"detail": "Workers are unavailable. Please try again later."},
                status=503,
            )
        return Response({"task_id": task_id.id})

    # hacky reimplementation of WorkerResponseConsumer.get_task_status()
    @extend_schema(
        responses={200: WorkerStatusResponseSerializer},
        parameters=[
            OpenApiParameter(
                "task_id", OpenApiTypes.UUID, OpenApiParameter.QUERY
            )
        ],  # type: ignore
    )
    @lookup.mapping.get
    def detail_lookup(self, request):
        task_id = request.query_params.get("task_id")
        task = process_geodata.AsyncResult(task_id)  # type: ignore
        try:
            task_user_slug = task.args[1]
        except IndexError:
            task_user_slug = None
        if task_user_slug != request.user.slug:
            return "PENDING", None
        response = task.result
        print(response)
        if not isinstance(response, dict):
            response = {"data": str(response)}
        serializer = WorkerStatusResponseSerializer(
            data={
                "status": task.status,
                "response": response,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
