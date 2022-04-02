from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from geodata.models import GeoData
from geodata.serializers import (
    GeoDataSerializer,
    AddressLookupSerializer,
    AddressLookupResponseSerializer,
)
from geodata.tasks import process_geodata


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
        task_id = process_geodata.s(address, request.user.id).apply_async()  # type: ignore
        return Response({"task_id": task_id.id})
