import requests
from django.core.management.base import BaseCommand
from sys import exit


class Command(BaseCommand):
    help = "Check if the API is up and running"

    def handle(self, *args, **options):
        try:
            response = requests.get("http://localhost:8000/status/")
            response.raise_for_status()
            if response.status_code == 200:
                print("OK")
                exit(0)
        except Exception:
            print("FAIL")
            exit(1)
