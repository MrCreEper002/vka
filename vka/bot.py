import asyncio
import json
from attrdict import AttrDict
from loguru import logger
from vka.base.longpoll import LongPoll
from vka.storage_box import storage_box
from vka.validator import Validator
import inspect
from typing import Iterable, List, Any
from datetime import datetime


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
        if ctx.msg.payload is not None:
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
            show_snackbar: str = None
    ):
        def wrapper(func):
            storage_box.commands.append(
                AttrDict(
                    {
                        'func_obj': func,
                        'any_text': any_text,
                        'names': names,
                        'prefixes': prefixes,
                        'lvl': lvl,
                        'show_snackbar': show_snackbar,
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
            # TODO Сделать чтобы по `prefixes` тоже работало
            # if command["prefixes"] is list:
            #     prefixes = ''.join([i for i in command['prefixes'] if ctx.msg.text.startswith(i)])
            if type(command['names']) is list:
                cmd = ''.join(
                    [
                        i
                        for i in command['names']
                        if i in ctx.msg.text.lower().split(
                                ' '
                            )[0:len(i.split(' '))]
                    ]
                )
                if cmd in command['names']:
                    ctx.cmd = cmd
                    await self._init_func(
                        func=command['func_obj'],
                        ctx=ctx,
                        argument=ctx.msg.text.replace(cmd, '').strip()
                    )
                continue
            else:
                cmd = ctx.msg.text.lower().split(
                    ' '
                )[0:len(command['names'].split(' '))]
            if command['names'] in cmd:
                ctx.cmd = command['names']
                await self._init_func(
                    func=command['func_obj'],
                    ctx=ctx,
                    argument=ctx.msg.text.lower().replace(
                        command['names'], ''
                    ).strip()
                )
                continue

    @staticmethod
    async def _init_func(
            func,
            ctx: Validator,
            argument: str
    ) -> asyncio.create_task:
        argument = argument if argument != '' else None
        argument = argument if argument != () else None
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
        except (KeyboardInterrupt, SystemExit):
            return
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
        Обрабатывает нового сообщения
        """
        return await self._check_message(
            Validator(
                bot=self, event=obj,
                api=self.api, group_id=self.group_id,
                receive=self._check,
                debug=self._debug,
                setup=self._state
            ),
            storage_box,
            # debug
        )

    async def _shipment_data_message_event(self, obj):
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

        saved_command = storage_box.callback_action.get(command)
        ctx = Validator(
                bot=self, event=obj,
                api=self.api, group_id=self.group_id,
                receive=self._check,
                debug=self._debug,
                setup=self._state
            )
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
            for func in storage_box.commands:
                if func.func_obj.__name__ == command:
                    ctx.cmd = func.names[-1] \
                        if type(func.names) is list \
                        else func.names

                    if func.show_snackbar is not None:
                        event_data['type'] = 'show_snackbar'
                        event_data['text'] = func.show_snackbar
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
                    gather.append(self._init_func(func.func_obj, ctx, argument))
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
    async def inspect_signature_executions(
            ctx: Validator, func, event_data: dict
    ):
        parameters = inspect.signature(
            func
        ).parameters
        if len(parameters) == 0:
            event_data['text'] = await func()
        else:
            event_data['text'] = await func(ctx)
        return event_data
