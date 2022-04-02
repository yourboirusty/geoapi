from datetime import datetime
import requests
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from geodata.models import FailedWorkerResult, IPSTACK_FIELDS
from geodata.serializers import (
    GeoDataSerializer,
    WorkerStatusResponseSerializer,
)
from celery.signals import (
    after_task_publish,
    task_postrun,
    task_prerun,
    task_retry,
)

from celery.app.task import Task
from celery.utils.log import get_task_logger

from celery import shared_task, states
from celery.exceptions import Ignore, BackendError


User = get_user_model()

URL = settings.IPSTACK_URL.rstrip("/")

REQUEST_PARAMS = {
    "access_key": settings.IPSTACK_KEY,
    "fields": ",".join(IPSTACK_FIELDS),
}

channel_layer = get_channel_layer()

logger = get_task_logger(__name__)


@shared_task(bind=True, name="geoapi.tasks.process_geodata", max_retries=4)
def process_geodata(self: Task, ip: str, user: str) -> str:  # type: ignore
    response = requests.get(f"{URL}/{ip}", params=REQUEST_PARAMS, timeout=2)
    try:
        user = User.objects.get(id=user)
    except User.DoesNotExist:
        logger.error(f"User {user} does not exist")
        self.update_state(state=states.FAILURE, meta="User does not exist")
        raise Ignore()
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        self.retry(exc=e)
    data = response.json()

    if not data.get("success"):
        self.retry(exc=BackendError(response.json()))

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
