import asyncio
import json

from loguru import logger
from attrdict import AttrDict
from vka.base.user import User
from vka.base.message import Message
from typing import Optional, List, Union, Dict, AsyncIterable
from vka.api import API, random_
from vka.storage_box import storage_box


class Validator:

    def __init__(
            self,
            bot, event,
            api: API,
            receive=None,
            type_message: str = '',
            debug: bool = False,
            setup=None,

    ):
        self._bot = bot
        self._event = event
        self._api = api
        self._receive = receive
        self._type_message = type_message
        self._debug = debug
        self._setup = setup
        self.cmd: str = ''

    async def receive_new_message(
            self,
            any_user: bool = False
    ) -> AsyncIterable["Validator"]:
        """
        Метод для получение нового сообщение

        По умолчанию реагирует на того пользователя который написал команду.
        -----------------------
        Пример использования

        ...     async for new_ctx in ctx.receive_new_message():
        ...         await new_ctx.reply('привет')

        -----------------------
        """
        while True:
            try:
                event = await self._receive()
                if event.updates and self._debug:
                    logger.debug(event)
                if event.updates:
                    obj = event.updates[0].object
                    type_message = event.updates[0].type
                    if type_message in ['message_new', 'message_event']:
                        if not any_user:
                            try:
                                from_id = obj.message.from_id
                            except:
                                from_id = obj.user_id
                            if self.msg.from_id == from_id:
                                yield Validator(
                                    bot=self._bot, event=obj,
                                    api=self.api, receive=self._receive,
                                    debug=self._debug, setup=self.setup
                                )
                        else:
                            yield Validator(
                                bot=self._bot, event=obj,
                                api=self.api, receive=self._receive,
                                debug=self._debug, setup=self.setup
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
            keyboard: Optional[Union[str, json.dumps]] = None,
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
            keyboard: Optional[Union[str, json.dumps]] = None,
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

    async def edit(
            self,
            message: str,
            conversation_message_id: int,
            *,
            message_id: Optional[int] = None,
            lat: Optional[float] = None,
            long: Optional[float] = None,
            attachment: Optional[List[Union[str]]] = None,
            keep_forward_messages: bool = 1,
            keep_snippets: bool = 1,
            keyboard: Optional[Union[str, json.dumps]] = None,
            dont_parse_links: bool = 1,
            template: Optional[Union[str]] = None,
            expire_ttl: Optional[int] = None,
    ):
        params = {"peer_id": self.msg.peer_id}
        return await self._messages_edit(locals(), params)

    async def transmit(
            self,
            message: str,
            **kwargs,
    ):
        if self.storage_box.messages_ids.get(self.msg.peer_id):
            return await self.edit(
                message,
                self.storage_box.messages_ids[self.msg.peer_id]['id'],
                **kwargs
            )
        else:
            try:
                getConversationsById = (
                    await self.api.messages.getConversationsById(
                        peer_ids=self.msg.peer_id
                    )
                ).response['items'][0]['last_conversation_message_id']
                message_id = getConversationsById

                if self.storage_box.messages_ids.get(self.msg.peer_id):
                    del self.storage_box.messages_ids[self.msg.peer_id]
                self.storage_box.messages_ids[self.msg.peer_id] = {
                    'id': message_id
                }
                return await self.edit(message, message_id, **kwargs)
            except:
                ...
        return await self.answer(message, **kwargs)

    async def fetch_sender(self, fields=None, name_case=None) -> User:
        """
        Обертка чтобы чтобы получить информацию об отправившем сообщениии

        ...     user = await ctx.fetch_sender()
        ...     await ctx.answer(f'Привет {user:fn}')

            id              - id
            fn              - имя
            ln              - фамилия
            full            - имя фамилия
            @ - [@id|name]  - делает упомнание
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
        return Message(self._event)


    @property
    def api(self) -> API:
        return self._api

    @property
    def event(self):
        return self._event

    @property
    def type_message(self) -> str:
        return self._type_message

    @property
    def setup(self):
        return self._setup

    async def _messages_send(self, locals_: locals, params: Dict) -> int:

        for name, value in locals_.items():
            if name == "kwargs":
                params.update(value)
            elif name != "self" and value is not None:
                params.update({name: value})

        del params["params"]
        params['random_id'] = random_()
        messages_id = await self.api.method("messages.send", params)
        if self.storage_box.messages_ids.get(self.msg.peer_id):
            del self.storage_box.messages_ids[self.msg.peer_id]
        self.storage_box.messages_ids[self.msg.peer_id] = {
            'id': messages_id.response
        }
        return messages_id.response

    async def _messages_edit(self, locals_: locals, params: Dict):

        for name, value in locals_.items():
            if name == "kwargs":
                params.update(value)
            elif name != "self" and value is not None:
                params.update({name: value})

        del params["params"]

        messages_id = await self.api.method("messages.edit", params)
        return messages_id

    @property
    def storage_box(self):
        return storage_box
