from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from geodata.models import GeoData
from geodata.serializers import GeoDataSerializer


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
