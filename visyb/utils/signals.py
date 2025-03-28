import inspect
import asyncio

class Signal:
    def __init__(self):
        self._listeners = []

    def connect(self, callback):
        self._listeners.append(callback)

    def disconnect(self, callback):
        self._listeners.remove(callback)

    async def emit(self, *args, **kwargs):
        for callback in self._listeners:
            if inspect.iscoroutinefunction(callback):
                await callback(*args, **kwargs)
            else:
                callback(*args, **kwargs)
