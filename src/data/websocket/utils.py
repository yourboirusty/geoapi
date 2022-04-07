import asyncio
from functools import wraps
from typing import Coroutine
from channels.generic.websocket import AsyncJsonWebsocketConsumer


MAX_RUNSTACK_SIZE = 10


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
