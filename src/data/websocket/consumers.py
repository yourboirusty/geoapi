from typing import Optional
from data.websocket.serializers import WorkerStatusResponseSerializer
from data.websocket.utils import StackedAsyncJsonWebsocketConsumer, close_stack
from data.tasks import process_geodata


class WorkerResponseConsumer(StackedAsyncJsonWebsocketConsumer):
    @close_stack
    async def connect(self):
        if not (task_id := self.scope["url_route"]["kwargs"].get("task_id")):
            await self.close(code=400)
        await self.accept()
        self.task_id = task_id
        self._append_runstack(
            self.send(text_data=f"Connected to task {self.task_id}")
        )
        self._append_runstack(
            self.channel_layer.group_add(  # type: ignore
                self.task_id,
                self.channel_name,
            )
        )
        task_result = process_geodata.AsyncResult(self.task_id)  # type: ignore
        self.send_status(
            status=task_result.status, response=task_result.result
        )

    async def disconnect(self, close_code):
        await self._await_stack()
        self._clean_stack()
        self.channel_layer.group_discard(  # type: ignore
            self.task_id,
            self.channel_name,
        )

    def send_status(
        self, status: str, response: Optional[str] = None, close=False
    ) -> None:
        serializer = WorkerStatusResponseSerializer(
            data={
                "status": status,
                "response": "None"
                if response is None
                else response,  # allow_blank is being ignored (??)
            }
        )
        if serializer.is_valid():
            self._append_runstack(self.send_json(serializer.data, close))
        else:
            self._append_runstack(self.send_json(serializer.errors, close))

    @close_stack
    async def worker_status(self, event: dict):
        self.send_status(event["status"], event.get("response"))
