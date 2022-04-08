from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.crypto import get_random_string

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    slug = models.SlugField(max_length=8)
    task_id = models.CharField(max_length=100, blank=True)


@receiver(pre_save, sender=User)
def pre_save_slug(sender, instance: User, *args, **kwargs):
    if instance.pk:
        return
    for x in range(50):
        instance.slug = get_random_string(
            length=8, allowed_chars=settings.SLUG_CHARACTERS
        )
        if not sender.objects.filter(slug=instance.slug).exists():
            break
        if x == 49:
            raise Exception("Could not generate unique slug")
