from vka import API
from vka.base.wrapper import Event


class Context:

    def __init__(self, event: Event, api: API):
        self._api = api
        self._event = event

    async def answer(self): ...

    async def reply(self): ...

    async def edit(self): ...

    # async def transmit(self): ...

    @property
    def api(self) -> API:
        return self._api

    @property
    def event(self) -> Event:
        return self._event


