import asyncio
from typing import Coroutine, Optional
from geodata.serializers import WorkerStatusResponseSerializer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from geodata.tasks import process_geodata
from functools import wraps

MAX_RUNSTACK_SIZE = 10


# TODO: Yeet this outta here
class StackedAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    _max_runstack_size = MAX_RUNSTACK_SIZE

    def __init__(self, *args, **kwargs):
        self._runstack = []
        super().__init__(*args, **kwargs)

    async def _await_stack(self):
        await asyncio.gather(*self._runstack)

    def _clean_stack(self):
        self._runstack = []

    def _append_runstack(self, coroutine: Coroutine) -> int:
        """Appends a coroutine to the running stack.
        Returns the index of the coroutine in the stack.
        """
        if len(self._runstack) >= self._max_runstack_size:
            raise RuntimeError(
                f"Runstack size exceeded. Max size is {self._max_runstack_size}"  # noqa E501
            )
        self._runstack.append(coroutine)
        return len(self._runstack) - 1

    def _pop_runstack(self, index: int) -> Coroutine:
        """Pops a coroutine from the running stack.
        Returns the popped coroutine.
        """
        return self._runstack.pop(index)

    def _get_runstack_size(self) -> int:
        return len(self._runstack)


def close_stack(f):
    @wraps(f)
    async def inner(self: StackedAsyncJsonWebsocketConsumer, *args, **kwargs):
        try:
            return await f(self, *args, **kwargs)
        finally:
            await asyncio.gather(*self._runstack)
            self._clean_stack()

    return inner


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
