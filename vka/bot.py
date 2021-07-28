import asyncio
import json
from attrdict import AttrDict
from loguru import logger
from vka.base.longpoll import LongPoll
from vka.storage_box import storage_box
from vka.validator import Validator
import inspect
from typing import Iterable, List, Any


class Commands:

    @staticmethod
    def click_callback(
            callback: bool = False,
            show_snackbar: bool = False,
            # open_link: bool = False,
            # open_app: bool = False
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
                storage_box.callback_action[func.__name__] = {
                    'func_obj': func,
                    'callback': callback,
                    'show_snackbar': show_snackbar
                }
                return func

            return wrapper()

        return decorator

    @staticmethod
    def click(func):
        """
        вешается на функцию где нужно чтобы потом вроверить нажалась ли эта кнопка
        """

        def wrapper():
            storage_box.callback_action[func.__name__] = {
                'func_obj': func,
                'click': True
            }
            return func

        return wrapper()

    @staticmethod
    def checking(
            func_name: object,
            ctx: [Validator, AttrDict],
            any_user: List,
    ) -> bool:
        """
        Проверяем нажали ли на кнопку, если да то возвращает True иначе False
        :param any_user:

        Нажата была некоторыми пользователями
            [False, [1,2,4]]
        Нажата была любым пользователем
            [True, ...]
        :param func_name: объект функции
        :param ctx: передавать Validator
        """
        if ctx.msg.get('payload'):
            command = eval(str(ctx.msg.payload))
            if any_user[0] is True and \
                    (len(any_user) == 1 or any_user[1] is Ellipsis):
                if func_name.__name__ == command['command']:
                    return True
            elif any_user[0] is False and type(any_user[1]) is list:
                try:
                    from_id = ctx.msg.from_id
                except:
                    from_id = ctx.msg.user_id
                if func_name.__name__ == command['command'] \
                        and from_id in any_user[1]:
                    return True
        return False

    @staticmethod
    def command(
            names: Iterable[str] = (),
            prefixes: Iterable[str] = (),
            any_text: bool = False,
            lvl: Any = None,
    ):
        def wrapper(func):
            storage_box.commands.append(
                AttrDict(
                    {
                        'func_obj': func,
                        'any_text': any_text,
                        'names': names,
                        'prefixes': prefixes,
                        'lvl': lvl
                    }
                )
            )
            return func

        return wrapper

    async def _check_message(
            self,
            ctx: Validator,
            storage: storage_box
    ) -> None:
        for command in storage.commands:
            if command['any_text']:
                asyncio.create_task(command['func_obj'](ctx))
                continue
            cmd = ctx.msg.text[0:len(command['names']):]
            if cmd == command['names']:
                ctx.cmd = cmd
                await self._init_func(
                    func=command['func_obj'],
                    ctx=ctx,
                    argument=ctx.msg.text.replace(cmd, '').strip()
                )
                continue

    @staticmethod
    async def _init_func(
            func,
            ctx: Validator,
            argument: str
    ) -> asyncio.create_task:
        argument = argument if argument != '' else None
        parameters = inspect.signature(func).parameters
        if len(parameters) == 0 and argument is None:
            return asyncio.create_task(func())
        elif len(parameters) == 1 and argument is None:
            return asyncio.create_task(func(ctx))
        elif len(parameters) == 2:
            return asyncio.create_task(func(ctx, argument))
        else:
            return


class Bot(LongPoll, Commands):

    def run(self, debug: bool = False, setup=None) -> None:
        self._debug = debug
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._async_run(setup))
            loop.close()
        except KeyboardInterrupt:
            pass
        logger.warning('Остановка бота')

    async def _async_run(self, setup):
        """
        Производит запуск бота
        """
        if setup is not None:
            asyncio.create_task(setup(self))
        self.group_id = (
            await self.api.method('groups.getById', {})
        ).response[0].id
        await self._update_long_poll_server()
        logger.success(f"Запуск бота в группе -> @club{self.group_id}")

        while True:
            try:
                event = await self._check()
                if self._debug and event.updates:
                    logger.debug(event)
                if event.updates:
                    type_message = event.updates[0].type
                    obj = event.updates[0].object
                    if type_message == 'message_new':
                        if obj.message.get('payload'):
                            asyncio.create_task(
                                self._shipment_data_message_event(obj)
                            )
                            continue
                        asyncio.create_task(
                            self._shipment_data_new_message(obj)
                        )
                        continue
                    if type_message == 'message_event':
                        asyncio.create_task(
                            self._shipment_data_message_event(obj)
                        )
                        continue

            except asyncio.TimeoutError:
                continue
            except Exception as error:
                logger.exception(error)

    async def _shipment_data_new_message(self, obj):
        """
        Обрабатывает нового сообощения
        """
        return await self._check_message(
            Validator(
                self, obj,
                self.api,
                self._check,
                debug=self._debug,
                setup=self._state
            ),
            storage_box,
            # debug
        )

    async def _shipment_data_message_event(self, obj):
        """
        Обрабатывает нажатие на кнопку
        то есть если пользователь нажмет на кнопку то в функции может чтото выполнится
        эта функция не отвечает за показ выполнилось функция или нет
        """
        event_data = {}
        try:
            command = obj.payload.command
        except:
            command = eval(obj.message.payload)['command']

        saved_command = storage_box.callback_action.get(command)

        if saved_command:
            if saved_command.get('click'):
                return await self.inspect_signature_return(
                    saved_command['func_obj'], obj
                )
            if saved_command['callback']:
                return await self.inspect_signature_return(
                    saved_command['func_obj'], obj
                )
            if saved_command['show_snackbar']:
                event_data['type'] = 'show_snackbar'
                event_data = await self.inspect_signature_executions(
                    saved_command['func_obj'], obj, event_data
                )
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

    async def inspect_signature_return(self, func, obj):
        parameters = inspect.signature(
            func
        ).parameters
        if len(parameters) == 0:
            return await func()
        return await func(
            Validator(
                self, obj, self.api,
                self._check,
                debug=self._debug,
                setup=self._state
            )
        )

    async def inspect_signature_executions(
            self, func, obj, event_data
    ):
        parameters = inspect.signature(
            func
        ).parameters
        if len(parameters) == 0:
            event_data['text'] = await func()
        else:
            event_data['text'] = await func(
                Validator(
                    self, obj, self.api,
                    self._check,
                    debug=self._debug,
                    setup=self._state
                )
            )
        return event_data
