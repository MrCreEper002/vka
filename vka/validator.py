import asyncio
import json

from loguru import logger
from attrdict import AttrDict
# from vka.bot import Bot
from vka.base.user import User
from vka.api import random_
from vka.base.message import Message
from typing import Optional, List, Union, Dict, AsyncIterable
from vka.api import API


class Validator:

    def __init__(
            self,
            event,
            api: API,
            receive=None,
            type_message: str = ''
    ):
        self._event = event
        self._api = api
        self._receive = receive
        self._type_message = type_message

    async def receive_new_message(self, any_user=True) -> AsyncIterable["Validator"]:
        """
        Метод для получение нового сообщение

        async for new_ctx in ctx.receive_new_message():
            await new_ctx.reply('привет')
        """
        while True:
            try:
                event = await self._receive()
                if event.updates:
                    type_message = event.updates[0].type
                    obj = event.updates[0].object
                    if not any_user:
                        if self.msg.from_id == obj.message.from_id:
                            yield Validator(
                                obj,
                                self.api,
                                type_message=type_message
                            )
                    else:
                        yield Validator(
                            obj,
                            self.api,
                            type_message=type_message
                        )

            except asyncio.TimeoutError:
                continue
            except Exception as error:
                logger.exception(error)
                break

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

    async def fetch_sender(self, fields=None, name_case=None) -> User:
        """
        Обертка чтобы чтобы получить информацию об отправившем сообщениии

            user = await ctx.fetch_sender()
            await ctx.answer(f'Привет {user:fn}')

        id - id
        fn - имя
        ln - фамилия
        full - имя фамилия
        @ - [@id|name]
        """
        user_info = await self.api.method(
            "users.get", {
                "user_ids": self.msg.from_id,
                'fields': fields,
                'name_case': name_case
            }
        )
        return User(AttrDict(user_info['response'][0]))

    @property
    def msg(self) -> Message:
        return self._event.message

    @property
    def api(self) -> API:
        return self._api

    @property
    def event(self):
        return self._event

    @property
    def type_message(self) -> str:
        return self._type_message

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
