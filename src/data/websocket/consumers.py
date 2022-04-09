from typing import Optional, Tuple
from django.conf import settings
from data.websocket.serializers import (
    TaskLookupSerializer,
    WorkerStatusResponseSerializer,
)
from data.websocket.utils import StackedAsyncJsonWebsocketConsumer, close_stack
from data.tasks import process_geodata


class WorkerResponseConsumer(StackedAsyncJsonWebsocketConsumer):
    @close_stack
    async def connect(self):
        if not (user := self.scope.get("user")):
            await self.close(code=400)
            return
        await self.accept()
        self.user_slug = user["slug"]
        self.post_connect()

    @close_stack
    async def receive_json(self, content: dict, **kwargs):
        serializer = TaskLookupSerializer(data=content)
        if not serializer.is_valid():
            self.send_errors(serializer.errors)
            return
        self.task_id = serializer.validated_data["task_id"]  # type: ignore
        status, response = self.get_task_status()
        self.send_status(status, response)

    async def disconnect(self, close_code):
        await self._await_stack()
        self._clean_stack()
        try:
            self.channel_layer.group_discard(  # type: ignore
                self.user_slug,
                self.channel_name,
            )
        except AttributeError:
            pass
        await self.close(code=close_code)

    def post_connect(self):
        # Connect to a dedicated user channel
        self._append_runstack(
            self.channel_layer.group_add(  # type: ignore
                self.user_slug,
                self.channel_name,
            )
        )

    def get_task_status(self) -> Tuple[str, Optional[str | dict]]:
        task = process_geodata.AsyncResult(self.task_id)  # type: ignore
        status = str(task.status)
        response = task.result
        try:
            task_user = task.args[1]
        except IndexError:
            task_user = None
        if task_user != self.user_slug:
            return "PENDING", None
        return status, response

    def _send_debug_message(self, message: dict) -> None:
        if settings.DEBUG:
            type(message)
            self._send({"debug": dict(message)})

    def send_status(
        self, status: str, response: Optional[dict | str] = None, close=False
    ) -> None:
        # Workaround to serializer ignoring 'required=True'
        if not isinstance(response, dict):
            response = {"data": str(response)}
        serializer = WorkerStatusResponseSerializer(
            data={
                "status": status,
                "response": response,
            }
        )

        if serializer.is_valid():
            self._send(serializer.validated_data)
        else:
            self._send_debug_message(serializer.errors)

    def send_errors(self, errors: dict) -> None:
        self._send(
            {
                "status": "REQUEST_ERROR",
                "response": errors,
            }
        )

    @close_stack
    async def worker_status(self, event: dict):
        self.send_status(event["status"], event.get("response"))
