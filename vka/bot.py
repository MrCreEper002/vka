import asyncio
import json
from typing import Any
from loguru import logger
from vka.base import AttrDict
from vka.base.longpoll import LongPoll
from vka.base.wrapper import Event
from vka.chatbot.checking import CheckingMessageForCommand
from vka.chatbot.context import Context
import sys

sys.dont_write_bytecode = True


class ABot(LongPoll):

    def run(self, debug: bool = False):
        try:
            asyncio.run(self.async_run())
        except (KeyboardInterrupt, SystemExit):
            return

    async def async_run(self, debug: bool = False):
        await self._init()
        await self._launching_bot(debug)

    async def _launching_bot(self, debug: bool):
        async for event in self._listen():
            if event.updates:
                asyncio.create_task(self._wiretapping_type(event.updates, debug))

    async def _wiretapping_type(self, updates, debug: bool):
        """
        Сделать чтобы можно было самому дописывать какие события нужно ловить
        пример кода как можно сделать:
            match event.type:
                case types if types in ['message_new']:
                    types
        """
        for i in updates:
            if debug:
                logger.debug(i)
            event = Event(i)
            ctx = Context(event=event, api=self.api, bot=self)
            match i.type:
                case 'message_new':
                    logger.opt(colors=True).info(
                        f'<red>[New message]</red> '
                        f'<white>peer_id: {ctx.msg.peer_id}</white> '
                        f'<blue>from_id: https://vk.com/id{ctx.msg.from_id}</blue> '
                        f'<green>message: {ctx.msg.text}</green>'
                    )
                    if 'payload' in event.message:
                        asyncio.create_task(
                            self._shipment_data_message_event(ctx=ctx, obj=event.obj)
                        )
                        continue

                    check = CheckingMessageForCommand(ctx)
                    await check.check_message(self.__commands__)
                    continue
                case 'message_event':
                    logger.opt(colors=True).info(
                        f'<red>[Message event]</red> '
                        f'<blue>peer_id: {ctx.msg.peer_id} '
                        f'from_id: https://vk.com/id{ctx.msg.from_id}</blue> '
                        f'<green>message: {ctx.msg.text}</green>'
                    )
                    asyncio.create_task(
                        self._shipment_data_message_event(ctx=ctx, obj=event.obj)
                    )
                    continue

    async def _shipment_data_message_event(self, ctx: Context, obj):
        """
        Обрабатывает нажатие на кнопку
        то есть если пользователь нажмет на кнопку то в функции
        может что-то выполнится
        эта функция не отвечает за показ выполнилось функция или нет
        """
        event_data = {}
        try:
            command = obj.payload.command
            argument = obj.payload.args
        except (KeyError, AttributeError):
            try:
                argument = AttrDict(eval(obj.message.payload))
                command = eval(obj.message.payload)['command']
            except (KeyError, AttributeError):
                return

        saved_command = self.__callback_action__.get(command)

        if saved_command:
            if saved_command.get('click'):
                return await self._init_func(saved_command['func_obj'], ctx, argument)
            if saved_command['callback']:
                await self._init_func(saved_command['func_obj'], ctx, argument)
            if saved_command['show_snackbar']:
                event_data['type'] = 'show_snackbar'
                event_data = await self.inspect_signature_executions(
                    ctx, saved_command['func_obj'], event_data
                )
        else:
            gather = []
            for func in self.__commands__:
                if func['func_obj'].__name__ == command:
                    ctx.cmd = func['commands'][-1] \
                        if type(func['commands']) is list \
                        else func['commands']

                    if func['show_snackbar'] is not None:
                        event_data['type'] = 'show_snackbar'
                        event_data['text'] = func['show_snackbar']
                        gather.append(
                            self.api.method(
                                'messages.sendMessageEventAnswer',
                                {
                                    "event_id": obj.event_id,
                                    "user_id": obj.user_id,
                                    "peer_id": obj.peer_id,
                                    "event_data": json.dumps(event_data)
                                }
                            )
                        )
                    check = CheckingMessageForCommand(ctx)
                    gather.append(check._init_func(func['func_obj'], ctx, argument))
                    await asyncio.gather(*gather)
                    return

        if event_data == {}:
            return
        return await self.api.method(
            'messages.sendMessageEventAnswer',
            {
                "event_id": obj.event_id,
                "user_id": obj.user_id,
                "peer_id": obj.peer_id,
                "event_data": json.dumps(event_data)
            }
        )

    def command(
            self, *custom_filter,
            commands=(), any_text: bool = False,
            lvl: Any = None, show_snackbar: str = None,
            custom_answer: str = None
    ):
        def wrapper(func):
            self.register_command(
                func=func, *custom_filter, commands=commands,
                any_text=any_text, lvl=lvl, show_snackbar=show_snackbar,
                custom_answer=custom_answer
            )
            return func

        return wrapper

    def register_command(
            self, func, custom_filter=None,
            commands=(), any_text: bool = False,
            lvl: Any = None, show_snackbar: str = None,
            custom_answer: str = None
    ):
        self.__commands__.append(
            {
                'func_obj': func,
                'custom_filter': custom_filter,
                'any_text': any_text,
                'commands': commands,
                'lvl': lvl,
                'show_snackbar': show_snackbar,
                'custom_answer': custom_answer,
            }
        )

    def click_callback(
            self, *custom_filter,
            callback: bool = False,
            show_snackbar: bool = False,
    ):
        """
        :param callback:
        :param show_snackbar: исчезающее сообщение на экране

        в разработке:
            # :param open_link: открывает ссылку
            # :param open_app: открывает vk mini apps
        """

        def decorator(func):
            def wrapper():
                self.register_callback(
                    func=func, *custom_filter, callback=callback,
                    show_snackbar=show_snackbar
                )
                return func
            return wrapper()
        return decorator

    def register_callback(
            self,
            func, *custom_filter,
            callback: bool = False,
            show_snackbar: bool = False,
    ):
        self.__callback_action__[func.__name__] = {
            'func_obj': func,
            'custom_filter': custom_filter,
            'callback': callback,
            'show_snackbar': show_snackbar
        }