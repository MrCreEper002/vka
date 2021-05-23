import json

from loguru import logger

from vka.api import random_
from vka.base.message import Message
from typing import Optional, List, Union, Dict
from vka.api import API


class Validator:

    def __init__(self, event, api: API):
        self._event = event
        self._api = api

    @property
    def msg(self) -> Message:
        return self._event.message

    @property
    def api(self) -> API:
        return self._api

    @property
    def event(self):
        return self._event

    async def answer(
            self,
            message: Optional[str] = None,
            *,
            random_id: Optional[int] = None,
            lat: Optional[float] = None,
            long: Optional[float] = None,
            attachment: Optional[List[Union[str]]] = None,
            reply_to: Optional[int] = None,
            forward_messages: Optional[List[int]] = None,
            sticker_id: Optional[int] = None,
            group_id: Optional[int] = None,
            keyboard: Optional[Union[str]] = None,
            payload: Optional[str] = None,
            dont_parse_links: Optional[bool] = None,
            disable_mentions: bool = True,
            intent: Optional[str] = None,
            expire_ttl: Optional[int] = None,
            silent: Optional[bool] = None,
            subscribe_id: Optional[int] = None,
            content_source: Optional[str] = None,
            forward: Optional[str] = None,
            **kwargs
    ):
        params = {'peer_id': self.msg.peer_id}

        return await self._messages_send(locals(), params)

    async def reply(
        self,
        message: Optional[str] = None,
        *,
        random_id: Optional[int] = None,
        lat: Optional[float] = None,
        long: Optional[float] = None,
        attachment: Optional[List[Union[str]]] = None,
        sticker_id: Optional[int] = None,
        group_id: Optional[int] = None,
        keyboard: Optional[Union[str]] = None,
        payload: Optional[str] = None,
        dont_parse_links: Optional[bool] = None,
        disable_mentions: bool = True,
        intent: Optional[str] = None,
        expire_ttl: Optional[int] = None,
        silent: Optional[bool] = None,
        subscribe_id: Optional[int] = None,
        content_source: Optional[str] = None,
        **kwargs,
    ):
        params = {"peer_id": self.msg.peer_id}
        if self.msg.id:
            params["reply_to"] = self.msg.id
        else:
            params["forward"] = json.dumps({
                "is_reply": True,
                "conversation_message_ids": [
                    self.msg.conversation_message_id
                ],
                "peer_id": self.msg.peer_id,
            })
        return await self._messages_send(locals(), params)

    async def _messages_send(self, locals_: locals, params: Dict):

        for name, value in locals_.items():
            if name == "kwargs":
                params.update(value)
            elif name != "self" and value is not None:
                params.update({name: value})

        del params["params"]
        params['random_id'] = random_()
        messages_id = await self.api.method("messages.send", params)
        return messages_id

    def __format__(self, format_spec):
        print(format_spec)


