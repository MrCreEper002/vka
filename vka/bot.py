import asyncio
import json
from attrdict import AttrDict
from loguru import logger
from vka.base.longpoll import LongPoll
from vka.storage_box import storage_box
from vka.validator import Validator
import inspect
from typing import Iterable, List


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
                storage_box.callback_action.append(
                    AttrDict(
                        {
                            'func_obj': func,
                            'callback': callback,
                            'show_snackbar': show_snackbar,
                            # 'open_link': open_link,
                            # 'open_app': open_app
                        }
                    )
                )
                return func

            return wrapper()

        return decorator

    @staticmethod
    def click(func):
        """
        вешается на функцию где нужно чтобы потом вроверить нажалась ли эта кнопка
        """

        def wrapper():
            storage_box.callback_action.append(
                AttrDict(
                    {
                        'func_obj': func,
                        'click': True
                    }
                )
            )
            return func

        return wrapper()

    @staticmethod
    def checking(
            func_name: object,
            ctx: [Validator, AttrDict],
            any_user: List,
    ):
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
            if any_user[0] is True and (len(any_user) == 1 or any_user[1] is Ellipsis):
                if func_name.__name__ == command['command']:
                    return True
            elif any_user[0] is False and type(any_user[1]) is list:
                try:
                    from_id = ctx.msg.from_id
                except:
                    from_id = ctx.msg.user_id
                if func_name.__name__ == command['command'] and from_id in any_user[1]:
                    return True
        return False

    @staticmethod
    def command(
            names: Iterable[str] = (),
            prefixes: Iterable[str] = (),
            any_text: bool = False,
    ):
        def wrapper(func):
            storage_box.commands.append(
                AttrDict(
                    {
                        'func_obj': func,
                        'any_text': any_text,
                        'names': names,
                        'prefixes': prefixes
                    }
                )
            )
            return func

        return wrapper

    async def _check_message(
            self,
            ctx: Validator,
            storage: storage_box
    ):
        for command in storage.commands:
            if command['any_text']:
                # await self.init_func(command['func_obj'])
                asyncio.create_task(command['func_obj'](ctx))
                continue
            if command['names'] == ctx.msg.text:
                # await self.init_func(command['func_obj'])
                asyncio.create_task(command['func_obj'](ctx))

    async def _init_func(self, func):
        for name, argument in inspect.signature(func).parameters.items():
            if argument.annotation is Validator:
                print(argument, 1)
            else:
                print(argument, 2)
            # logger.info(f"{name} {argument.annotation} {argument.annotation is Validator}")


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
                            asyncio.create_task(self._shipment_data_message_event(obj))
                            continue
                        asyncio.create_task(
                            self._shipment_data_new_message(obj)
                        )
                        continue
                    if type_message == 'message_event':
                        asyncio.create_task(self._shipment_data_message_event(obj))
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
            Validator(self, obj, self.api, self._check, debug=self._debug, setup=self._state),
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

        for i in range(len(storage_box.callback_action)):
            if storage_box.callback_action[i].func_obj.__name__ == command:
                if storage_box.callback_action[i].get('click'):
                    parameters = inspect.signature(storage_box.callback_action[i].func_obj).parameters
                    if len(parameters) == 0:
                        return await storage_box.callback_action[i].func_obj()
                    return await storage_box.callback_action[i].func_obj(
                        Validator(self, obj, self.api, self._check, debug=self._debug, setup=self._state)
                    )
                if storage_box.callback_action[i].callback:
                    parameters = inspect.signature(storage_box.callback_action[i].func_obj).parameters
                    if len(parameters) == 0:
                        return await storage_box.callback_action[i].func_obj()
                    return await storage_box.callback_action[i].func_obj(
                        Validator(self, obj, self.api, self._check, debug=self._debug, setup=self._state)
                    )
                if storage_box.callback_action[i].show_snackbar:
                    event_data['type'] = 'show_snackbar'
                    parameters = inspect.signature(storage_box.callback_action[i].func_obj).parameters
                    if len(parameters) == 0:
                        event_data['text'] = await storage_box.callback_action[i].func_obj()
                        break
                    event_data['text'] = await storage_box.callback_action[i].func_obj(
                        Validator(self, obj, self.api, self._check, debug=self._debug, setup=self._state)
                    )
                    break

        if event_data == {}:
            return
        logger.success(1)
        return await self.api.method(
            'messages.sendMessageEventAnswer',
            {
                "event_id": obj.event_id,
                "user_id": obj.user_id,
                "peer_id": obj.peer_id,
                "event_data": json.dumps(event_data)
            }
        )
