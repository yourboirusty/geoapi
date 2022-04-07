import string

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string


User = get_user_model()

SLUG_CHARACTERS = string.ascii_uppercase + string.digits[2:]

IPSTACK_FIELDS = [
    "continent_name",
    "country_name",
    "region_name",
    "city",
    "latitude",
    "longitude",
]


class GeoDataSlugEnded(Exception):
    pass


# TODO: Does it even belong here? Should it be handled by logging instead?
class FailedWorkerResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255, blank=True, null=True)

    worker_name = models.CharField(max_length=255)
    worker_error = models.TextField()
    worker_result = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]


class GeoData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=8, blank=True)
    task_id = models.CharField(max_length=255)

    # Ideally this part would be noSQL, but it'll do
    address = models.CharField(max_length=15)
    continent_name = models.CharField(max_length=255)
    country_name = models.CharField(max_length=255)
    region_name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.address

    class Meta:
        db_table = "geodata"
        ordering = ["-timestamp"]


@receiver(pre_save, sender=GeoData)
def pre_save_slug(sender, instance: GeoData, *args, **kwargs):
    if instance.pk:
        return
    for x in range(50):
        instance.slug = get_random_string(
            length=8, allowed_chars=SLUG_CHARACTERS
        )
        # TODO: Figure out why this uses 3 db calls
        if not sender.objects.filter(slug=instance.slug).exists():
            break
        if x == 49:
            raise GeoDataSlugEnded
