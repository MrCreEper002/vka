import asyncio
from typing import Any
from loguru import logger

from vka.base.longpoll import LongPoll
from vka.base.wrapper import Event
from vka.chatbot.checking import CheckingEventForCommand
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
            run_custom_func = asyncio.create_task(custom_func(self))
            self.set_item(key='run_custom_func', value=run_custom_func)
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
        check = CheckingEventForCommand(
            ctx=ctx,
            menu_commands=self.__menu_commands__,
            callback_action=self.__callback_action__,
            commands=self.__commands__
        )
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
                    check.shipment_data_message_event(
                        obj=event.obj
                    )
                )
                return
            await check.search_for_command_message()

        elif update.type == 'message_event':
            logger.opt(colors=True).info(
                f'[vka {self.group_id}] '
                f'<red>type: Message event</red> '
                f'<white>peer_id: {ctx.msg.peer_id}</white> '
                f'<blue>from_id: '
                f'{ctx.msg.from_id}</blue> '
            )
            asyncio.create_task(
                check.shipment_data_message_event(
                    obj=event.obj,
                )
            )

    def add_command(
            self, *custom_filter,
            commands=(), any_text: bool = False,
            lvl: Any = None, show_snackbar: str = None,
            custom_answer: str = None
    ):
        """ используется декоратором над функцией """
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
        используется декоратором над функцией

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

