import asyncio
import json
from typing import Optional, List, Union, Dict, AsyncIterable
from loguru import logger
from vka import API, random_
from vka.base.wrapper import Event, Message
from vka.chatbot.wrappers.user import User


class Context:

    def __init__(self, event, api: API, bot):
        self._bot = bot
        self._api = api
        self._event = event
        self.command = ''

    @property
    def api(self) -> API:
        return self._api

    @property
    def event(self) -> Event:
        return self._event

    @property
    def msg(self) -> Message:
        return Message(self.event.obj)

    @property
    def bot(self) -> "ABot":
        return self._bot

    @property
    def group_id(self) -> int:
        return self.event.group_id

    async def receive_new_message(
            self,
            any_user: bool = False
    ) -> AsyncIterable["Context"]:
        """
        Метод для получение нового сообщение
        По умолчанию реагирует на того пользователя который написал команду.

        any_user: реагирует на любого человека

        Пример:
            >>> async for new_ctx in ctx.receive_new_message():
            >>>    await new_ctx.reply('привет')
        """
        async for new_event in self.receiving():
            if new_event.updates:
                for event in new_event.updates:
                    event = Event(event)
                    logger.success(event)
                    ctx = Context(event=event, api=self.api, bot=self)
                    if event.type in ['message_new', 'message_event']:
                        if any_user and ctx.msg.peer_id == self.msg.peer_id:
                            yield ctx
                        else:
                            if self.msg.from_id == ctx.msg.from_id \
                                    and ctx.msg.peer_id == self.msg.peer_id:
                                yield ctx

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
            dont_parse_links: Optional[int] = None,
            disable_mentions: bool = True,
            intent: Optional[str] = None,
            expire_ttl: Optional[int] = None,
            silent: Optional[bool] = None,
            subscribe_id: Optional[int] = None,
            content_source: Optional[str] = None,
            forward: Optional[str] = None,
            **kwargs
    ):
        if not kwargs.get('peer_id'):
            params = {'peer_id': self.msg.peer_id}
        else:
            params = {}
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
        if not kwargs.get('peer_id'):
            params = {'peer_id': self.msg.peer_id}
        else:
            params = {}
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
            conversation_message_id: int = None,
            # *,
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
            **kwargs
    ):
        if not kwargs.get('peer_id'):
            params = {'peer_id': self.msg.peer_id}
        else:
            params = {}
        return await self._messages_edit(locals(), params)

    async def transmit(
            self,
            message: str,
            **kwargs,
    ):
        # TODO Переписать или удалить!
        """
        данная функция означает что будет изменено последнее сообщение бота
        """
        await self.edit(
            message,
            self.msg.conversation_message_id,
            **kwargs
        )

    async def fetch_sender(
            self,
            fields: List[str] = None,
            name_case: str = None,
            **kwargs
    ) -> list[User] | None | User:
        """
        Обертка чтобы чтобы получить информацию об сообщении о его отправители
        По умолчанию получает айди отправителя

        fields: подробное описание написано тут https://dev.vk.com/reference/objects/user

        name_case:
            • именительный – nom,
            • родительный – gen,
            • дательный – dat,
            • винительный – acc,
            • творительный – ins,
            • предложный – abl.

        kwargs:
            • replay=True: если на сообщение было отвечено;
            • fwd=True: если на сообщение было переслано;
            • all=True: все эти параметры сразу;

        Пример:
            >>> user = await ctx.fetch_sender()
            >>> await ctx.answer(f'Привет {user:fn}')

            • id              - id
            • fn              - имя
            • ln              - фамилия
            • full            - имя фамилия
            • @               - делает упоминание
        """
        if kwargs.get('reply'):
            try:
                user_ids = self.msg.reply_message.from_id
            except:
                return []
        elif kwargs.get('fwd'):
            try:
                user_ids = [fwd.from_id for fwd in self.msg.fwd_messages]
            except:
                return []
        elif kwargs.get('all'):
            user_ids = []
            try:
                user_ids.append(self.msg.reply_message.from_id)
            except: ...
            try:
                [
                    user_ids.append(user.from_id)
                    for user in self.msg.fwd_messages if user.from_id > 0
                ]
            except: ...
            user_ids.append(self.msg.from_id)
        else:
            user_ids = self.msg.from_id

        users_info = await self.api.method(
            "users.get", {
                "user_ids": user_ids,
                'fields': fields,
                'name_case': name_case
            }
        )
        if users_info == ():
            return []
        elif isinstance(user_ids, int):
            return User(users_info[0])
        elif len(users_info) == 1:
            return User(users_info[0])
        return [User(user) for user in users_info]

    async def user_get(
            self,
            user_ids: list | int | str,
            fields: List[str] = None,
            name_case: str = None
    ):
        """
        Обертка чтобы чтобы получить информацию об юзер айди, которые были переданы
        Про fields, name_case можно прочесть в методе fetch_sender
        """
        users_info = await self.api.method(
            "users.get", {
                "user_ids": user_ids,
                'fields': fields,
                'name_case': name_case
            }
        )
        if isinstance(user_ids, int) or isinstance(user_ids, str):
            try:
                return User(users_info[0])
            except IndexError:
                ...
        return [User(user) for user in users_info]

    def button_checking(
            self,
            func_name: object,
            any_user: [int, list, Ellipsis],
    ) -> bool:
        """
        Проверяем нажали ли на кнопку, если да то возвращает True иначе False
        :param any_user:
            1     - только если этим юзером
            [1,2] - только если этими юзерами
            ...   - всеми

        :param func_name: объект функции

        Пример:
            async for new_ctx in ctx.receive_new_message():
                if new_ctx.button_checking(obj, ...):
                    await new_ctx.answer('Ты нажал на кнопку')
        """
        if self.msg.payload is not None:
            command = eval(str(self.msg.payload))
            if func_name.__name__ == command['command']:
                if isinstance(any_user, int):
                    if self.msg.from_id == any_user:
                        return True
                elif isinstance(any_user, list):
                    if self.msg.from_id in any_user:
                        return True
                elif any_user is Ellipsis:
                    return True
            return False
        return False

    async def _messages_send(self, locals_: locals, params: Dict) -> dict:
        params = check_params(locals_=locals_, params=params)

        params['random_id'] = random_()
        messages_id = await self.api.method("messages.send", params)
        return messages_id

    async def _messages_edit(self, locals_: locals, params: Dict) -> dict:
        params = check_params(locals_=locals_, params=params)

        messages_id = await self.api.method("messages.edit", params)
        return messages_id

    async def receiving(self):
        while True:
            try:
                yield await self.bot._check()
            except asyncio.TimeoutError:
                continue
            except Exception as vka_error:
                logger.error(vka_error)
                continue

    async def for_receiving(self, new_event, any_user):
        for event in new_event:
            logger.warning(event)
            event = Event(event)
            ctx = Context(event=event, api=self.api, bot=self)

            match event.type:
                case ['message_new', 'message_event']:
                    if any_user:
                        yield ctx
                    else:
                        if self.msg.from_id in ctx.msg.from_id:
                            yield ctx


def check_params(locals_: locals, params: dict) -> dict:
    for name, value in locals_.items():
        if name == "kwargs":
            params.update(value)
        elif name != "self" and value is not None:
            params.update({name: value})

    del params["params"]
    return params
