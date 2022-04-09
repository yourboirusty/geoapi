from datetime import datetime
import requests
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from data.models import IPSTACK_FIELDS
from data.serializers import (
    GeoDataSerializer,
)
from authentication.models import User
from data.websocket.serializers import (
    WorkerStatusResponseSerializer,
)
from celery.signals import (
    after_task_publish,
    task_postrun,
    task_prerun,
    task_retry,
)

from typing import Type
from celery.app.task import Task
from celery.utils.log import get_task_logger

from celery import shared_task, states
from celery.exceptions import Ignore, BackendError


URL = settings.IPSTACK_URL.rstrip("/")

REQUEST_PARAMS = {
    "access_key": settings.IPSTACK_KEY,
    "fields": ",".join(IPSTACK_FIELDS),
}

channel_layer = get_channel_layer()  # type: ignore
if not channel_layer:
    raise RuntimeError("Channel layer not found")

logger = get_task_logger(__name__)


# TODO: Cleanup
@shared_task(
    bind=True,
    name="geoapi.tasks.process_geodata",
    max_retries=2,
    default_retry_delay=2,
)
def process_geodata(self: Task, ip: str, user_slug: str) -> str:  # type: ignore # noqa E501
    user = login_user(self, user_slug)

    data = get_geodata_from_ip(self, ip)

    data.update({"address": ip, "user": user.id, "task_id": self.request.id})
    serializer = GeoDataSerializer(data=data)
    if serializer.is_valid():
        try:
            geodata_object = serializer.save()
            return geodata_object.slug
        except Exception as e:
            logger.error(f"Cannot write to database: {e}")
            self.update_state(
                state=states.FAILURE,
                meta={"reason": "Cannot write to database"},
            )
            raise Ignore()
    else:
        self.retry(exc=BackendError(serializer.errors))


def get_geodata_from_ip(self, ip):
    response = requests.get(f"{URL}/{ip}", params=REQUEST_PARAMS, timeout=2)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        self.retry(exc=e)
    data = response.json()

    # Success can only be false (???)
    if not data.get("success", True):
        self.retry(exc=BackendError(response.json()))
    return data


def login_user(self, user_slug: str) -> Type[User]:
    try:
        user = User.objects.get(slug=user_slug)
    except User.DoesNotExist:
        logger.error(f"User {user_slug} does not exist")
        self.update_state(state=states.FAILURE, meta="User does not exist")
        raise Ignore()
    return user


def send_worker_status(user_slug: str, data: dict) -> None:
    serializer = WorkerStatusResponseSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    async_to_sync(channel_layer.group_send)(  # type: ignore
        user_slug,
        {
            "type": "worker_status",
            "timestamp": datetime.now().isoformat(),
            **serializer.validated_data,
        },
    )


# TODO: Cleanup
@after_task_publish.connect(sender="geoapi.tasks.process_geodata")
def task_sent_handler(headers: dict, **kwargs):
    send_worker_status(headers["id"], {"status": "created"})


@task_prerun.connect(sender="geoapi.tasks.process_geodata")
def task_received_handler(args, **kwargs):
    send_worker_status(args[1], {"status": states.RECEIVED})


@task_postrun.connect(sender="geoapi.tasks.process_geodata")
def task_postrun_handler(args, state, retval, **kwargs):
    send_worker_status(args[1], {"status": state, "response": str(retval)})


@task_retry.connect(sender="geoapi.tasks.process_geodata")
def task_retry_handler(request, reason, **kwargs):
    print(request)
    print(f"Retrying task {request.args[1]}")
    async_to_sync(send_worker_status)(
        request.args[1], {"status": states.RETRY, "response": str(reason)}
    )
