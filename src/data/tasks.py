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
@shared_task(bind=True, name="geoapi.tasks.process_geodata", max_retries=4)
def process_geodata(self: Task, ip: str, user_slug: str) -> str:  # type: ignore # noqa E501
    user = login_user(self, user_slug)

    data = get_geodata_from_ip(self, ip)

    data.update({"address": ip, "user": user, "task_id": self.request.id})
    serializer = GeoDataSerializer(data=data)
    if serializer.is_valid():
        try:
            geodata_object = serializer.save()
            return geodata_object.slug
        except Exception as e:
            logger.error(f"Cannot write to database: {e}")
            self.update_state(
                state=states.FAILURE, meta="Cannot write to database"
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

    if not data.get("success"):
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


async def send_worker_status(task_id: str, data: dict) -> None:
    serializer = WorkerStatusResponseSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    await channel_layer.group_send(  # type: ignore
        task_id,
        {
            "type": "worker_status",
            "timestamp": datetime.now().isoformat(),
            "status": serializer.data,
        },
    )


# TODO: Merge this mess to one, clean function
# (multiple decorators? use a signal for status changes?)
@after_task_publish.connect(sender="geoapi.tasks.process_geodata")
def task_sent_handler(headers: dict, **kwargs):
    async_to_sync(send_worker_status)(headers["id"], {"status": "created"})


@task_prerun.connect(sender="geoapi.tasks.process_geodata")
def task_received_handler(task_id, **kwargs):
    async_to_sync(send_worker_status)(task_id, {"status": "running"})


@task_postrun.connect(sender="geoapi.tasks.process_geodata")
def task_postrun_handler(task_id, state, retval, **kwargs):
    async_to_sync(send_worker_status)(
        task_id, {"status": state.lower, "retval": retval}
    )


@task_retry.connect(sender="geoapi.tasks.process_geodata")
def task_retry_handler(request, reason, **kwargs):
    async_to_sync(send_worker_status)(
        request.task_id, {"status": "retrying", "reason": str(reason)}
    )
