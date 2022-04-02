from geodata.serializers import GeoDataSerializer
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import urlparse
from dataclasses import dataclass


class WorkerResponseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not (task_id := self.scope["url_route"]["kwargs"].get("task_id")):
            await self.close(code=400)
        await self.accept()
        await self.send(text_data=f"Connected to task {task_id}")

    async def disconnect(self, close_code):
        pass

    async def client_status(self, event):
        await self.send(text_data=event["status"])

    async def worker_status(self, event):
        await self.send(text_data=event["status"])
