from loguru import logger

from vka.base.attrdict import AttrDict
from vka.chatbot.wrappers.messege import Message


class EventBase:
    def __init__(self, event):
        self._event = event
        self._ts: str = event.ts
        self._updates: list = event.updates

    @property
    def ts(self) -> str:
        return self._ts

    @property
    def updates(self) -> list['Event']:
        return self._updates

    def __repr__(self):
        return f"{self._event}"


class Event:
    def __init__(self, event):
        self._event = event

    @property
    def type(self) -> str:
        return self._event.type

    @property
    def obj(self) -> AttrDict:
        return self._event.object

    @property
    def message(self) -> Message:
        return self.obj.message

    @property
    def group_id(self) -> int:
        return self._event.group_id

    @property
    def event_id(self) -> str:
        return self._event.event_id

    def __repr__(self):
        return f'{self._event}'

