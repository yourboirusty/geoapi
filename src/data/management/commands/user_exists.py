from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from sys import exit


class Command(BaseCommand):
    help = "Check if root user exists"

    def handle(self, *args, **options):
        try:
            x = get_user_model().objects.get(username="root")
            if x.slug:
                print("OK")
                exit(0)
        except Exception:
            print("FAIL")
            exit(1)
