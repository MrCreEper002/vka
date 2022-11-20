import asyncio
import inspect
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

    """
    param debug:
        Включение debug режима
    param custom_event_name:
        Чтобы бот мог отловить другое событие
        [
            'wall_post_new', 'message_edit'
        ]
    param custom_event_func:
        ctx - обязательный параметр
        async def custom_event_func(ctx: Context): ...
    param custom_func:
        async def custom_func(bot: ABot): ...

    """

    def run(
            self, debug: bool = False,
            custom_event_name: list[str] = None,
            custom_event_func=None,
            custom_func=None
    ):
        try:
            asyncio.run(
                self.async_run(
                    debug=debug,
                    custom_event_name=custom_event_name,
                    custom_event_func=custom_event_func,
                    custom_func=custom_func,
                )
            )
        except (KeyboardInterrupt, SystemExit):
            return

    async def async_run(
            self, debug: bool = False,
            custom_event_name: list[str] = None,
            custom_event_func=None,
            custom_func=None,
    ):
        await self.async_init()
        self.custom_event_name = custom_event_name
        self.custom_event_func = custom_event_func
        if custom_func is not None:
            asyncio.create_task(custom_func(self))
        await self._launching_bot(debug)

    async def _launching_bot(
            self, debug: bool,
    ):
        async for event in self.listen():
            if event.updates:
                asyncio.create_task(
                    self._wiretapping_type(
                        updates=event.updates, debug=debug
                    )
                )

    async def _wiretapping_type(
            self, updates, debug: bool,
    ):
        for i in updates:
            if debug:
                logger.opt(colors=True).debug(
                    f'[vka {self.group_id}] {i}'
                )
            await self._defining_events(update=i)

    async def _defining_events(self, update):
        """
        Определяем какой событие пришло от сервера
        """
        event = Event(update)
        ctx = Context(event=event, api=self.api, bot=self)
        if self.custom_event_name is not None and update.type in self.custom_event_name:
            if self.custom_event_func is not None:
                return await self.custom_event_func(ctx)
        elif update.type == 'message_new':
            logger.opt(colors=True).info(
                f'[vka {self.group_id}] '
                f'<red>type: New message</red> '
                f'<white>peer_id: {ctx.msg.peer_id}</white> '
                f'<blue>from_id: '
                f'{ctx.msg.from_id}</blue> '
                f'<green>message: {ctx.msg.text}</green>'
            )
            if 'payload' in event.message:
                asyncio.create_task(
                    self._shipment_data_message_event(
                        ctx=ctx, obj=event.obj
                    )
                )
                return
            check = CheckingMessageForCommand(ctx)
            await check.check_message(self.__commands__)
        elif update.type == 'message_event':
            logger.opt(colors=True).info(
                f'[vka {self.group_id}] '
                f'<red>type: Message event</red> '
                f'<white>peer_id: {ctx.msg.peer_id}</white> '
                f'<blue>from_id: '
                f'{ctx.msg.from_id}</blue> '
            )
            asyncio.create_task(
                self._shipment_data_message_event(
                    ctx=ctx, obj=event.obj
                )
            )

    async def _shipment_data_message_event(self, ctx: Context, obj):
        """
        Обрабатывает нажатие на кнопку
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
        check = CheckingMessageForCommand(ctx)
        if saved_command:
            if saved_command.get('click'):
                return await check.init_func(
                    saved_command['func_obj'], ctx, command=command, argument=argument
                )
            if saved_command['callback']:
                await check.init_func(
                    saved_command['func_obj'], ctx, command=command, argument=argument
                )
            if saved_command['show_snackbar']:
                argument = argument if argument != '' else None
                argument = argument if argument != () else None
                event_data['type'] = 'show_snackbar'
                event_data = await self._inspect_signature_executions(
                    ctx, saved_command['func_obj'], event_data,
                    argument=argument
                )
        else:
            gather = []
            for func in self.__commands__:
                if func['func_obj'].__name__ == command:
                    # ctx.cmd = func['commands'][-1] \
                    #     if type(func['commands']) is list \
                    #     else func['commands']

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
                    gather.append(
                        check.init_func(func['func_obj'], ctx, command=command, argument=argument)
                    )
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

    @staticmethod
    async def _inspect_signature_executions(
            ctx: Context, func, event_data: dict, argument: str
    ):
        parameters = inspect.signature(
            func
        ).parameters
        if len(parameters) == 0:
            event_data['text'] = await func()
        elif len(parameters) == 1:
            event_data['text'] = await func(ctx)
        else:
            event_data['text'] = await func(ctx, argument)
        return event_data

    def add_command(
            self, *custom_filter,
            commands=(), any_text: bool = False,
            lvl: Any = None, show_snackbar: str = None,
            custom_answer: str = None
    ):
        """ используется декоратором на функцией """
        def wrapper(func):
            self.register_command(
                func=func, *custom_filter, commands=commands,
                any_text=any_text, lvl=lvl, show_snackbar=show_snackbar,
                custom_answer=custom_answer
            )
            return func

        return wrapper

    def register_command(
            self, func, *custom_filter,
            commands=(), any_text: bool = False,
            lvl: Any = None, show_snackbar: str = None,
            custom_answer: str = None,
    ):
        """
        Регистрирует команду в боте
        :param func: сама функция команды
        :param custom_filter: свой фильтр
        :param commands: команды | str / [str, ...]
        :param any_text: любой текст | bool
        :param lvl: дополнительный аргумент
        :param show_snackbar:
        :param custom_answer:
        :return:
        """
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

    def add_click_callback(
            self, *custom_filter,
            callback: bool = False,
            show_snackbar: bool = False,
    ):
        """
        используется декоратором на функцией

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
            show_snackbar: bool | str = False,
    ):
        """ можно использовать для добавлении кнопок без декораторов """
        self.__callback_action__[func.__name__] = {
            'func_obj': func,
            'custom_filter': custom_filter,
            'callback': callback,
            'show_snackbar': show_snackbar
        }

