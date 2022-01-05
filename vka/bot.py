import asyncio
from typing import Any, Iterable
from loguru import logger
from vka.base.longpoll import LongPoll
from vka.base.wrapper import Event
from vka.chatbot import KeyAndBoxStorage
from vka.chatbot.checking import CheckingMessageForCommand
from vka.chatbot.context import Context


class ABot(KeyAndBoxStorage, LongPoll):

    def run(self):
        try:
            asyncio.run(self._launching_bot())
        except (KeyboardInterrupt, SystemExit):
            return

    async def async_run(self):
        await self._launching_bot()

    async def _launching_bot(self, ):
        await self._init()

        async for event in self._listen():
            if event.updates:
                await self._wiretapping_type(event.updates)

    async def _wiretapping_type(self, updates):
        """
        Сделать чтобы можно было самому дописывать какие события нужно ловить
        пример кода как можно сделать:
            match event.type:
                case types if types in ['message_new']:
                    types
        """
        for i in updates:
            event = Event(i)
            logger.info(event)
            match event.type:
                case 'message_new':
                    ctx = Context(event, self.api)
                    check = CheckingMessageForCommand(ctx)
                    await check.check_message(self.__commands__)
                case 'message_event':
                    ...

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
            self, func, *custom_filter,
            commands, any_text: bool = False,
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