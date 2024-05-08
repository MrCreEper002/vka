import asyncio
from typing import Any, Callable
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
        self.debug = debug
        await self.async_init()
        self.custom_event_name = custom_event_name
        self.custom_event_func = custom_event_func
        if custom_func is not None:
            run_custom_func = asyncio.create_task(custom_func(self))
            self.set_item(key='run_custom_func', value=run_custom_func)
        await self._launching_bot()

    async def _launching_bot(
            self,
    ):
        async for event in self.listen():
            if event.updates:
                asyncio.create_task(
                    self._wiretapping_type(
                        updates=event.updates
                    )
                )

    async def _wiretapping_type(
            self, updates
    ):
        for i in updates:
            if self.debug:
                logger.opt(record=False, colors=True).log(
                    self.name_bot,
                    f'<b><blue>[Debug] {i}</blue></b>'
                )
            await self._defining_events(update=i)

    async def _defining_events(self, update):
        """
        Определяем какое событие пришло от сервера
        """
        event = Event(update)
        ctx = Context(event=event, api=self.api, bot=self)
        check = CheckingEventForCommand(
            ctx=ctx,
            menu_commands=self.__menu_commands__,
            callback_action=self.__callback_action__,
            commands=self.__commands__
        )
        peer_id = ''
        if ctx.msg.get('peer_id') is not None and ctx.msg.peer_id != ctx.msg.from_id:
            peer_id = f'<fg #999999>peer_id: {ctx.msg.peer_id}</fg #999999> '
        if (self.custom_event_name is not None
                and update.type in self.custom_event_name):
            if self.custom_event_func is not None:
                return await self.custom_event_func(ctx)
        elif update.type == 'message_new':

            text = f"{ctx.msg.text[0:15]}..." \
                if len(ctx.msg.text) > 15 \
                else ctx.msg.text

            logger.opt(record=True, colors=True).log(
                self.name_bot,
                f'<b><y>[New message]</y></b> '
                f'{peer_id}'
                f'<fg #999999>from_id: {ctx.msg.from_id}</fg #999999> '
                f'<fg #ffffff>message: {text}</fg #ffffff> '
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
            logger.opt(record=True, colors=True).log(
                self.name_bot,
                f'<b><y>[Message event]</y></b> '
                f'{peer_id}'
                f'<fg #999999>from_id: {ctx.msg.from_id}</fg #999999> '
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
            self, func: Callable[[Context], Any], *custom_filter,
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
            func: Callable[[Context], Any], *custom_filter,
            callback: bool = False,
            show_snackbar: bool | str = False,
    ):
        """ если проект разбит на файлы проще использовать """
        self.__callback_action__[func.__name__] = {
            'func_obj': func,
            'custom_filter': custom_filter,
            'callback': callback,
            'show_snackbar': show_snackbar
        }
