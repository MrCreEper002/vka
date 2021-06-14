import asyncio
from loguru import logger
# from vka.command import Commands
from vka.longpoll import LongPoll
from vka.storage_box import storage_box
from vka.validator import Validator
import inspect
from typing import Iterable


class Commands:
    @staticmethod
    def command(
            names: Iterable[str] = (),
            prefixes: Iterable[str] = (),
            any_text: bool = False,
    ):
        def wrapper(func):
            storage_box.commands.append(
                {
                    'func_obj': func,
                    'any_text': any_text,
                    'names': names,
                    'prefixes': prefixes
                }
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

    async def init_func(self, func):

        for name, argument in inspect.signature(func).parameters.items():
            if argument.annotation is Validator:
                print(argument, 1)
            else:
                print(argument, 2)
            # logger.info(f"{name} {argument.annotation} {argument.annotation is Validator}")


class Bot(LongPoll, Commands):

    def run(self, debug: bool = False) -> None:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._async_run(debug))
            loop.close()
        except KeyboardInterrupt:
            pass
        logger.warning('Остановка бота')

    async def _async_run(self, debug):
        self.group_id = (
            await self.api.method('groups.getById', {})
        ).response[0].id
        await self._update_long_poll_server()
        logger.success(f"Запуск бота в группе -> @club{self.group_id}")

        while True:
            try:
                event = await self._check()
                if debug and event.updates:
                    logger.debug(event)
                if event.updates:
                    logger.warning(self._storage_box.commands)
                    type_message = event.updates[0].type
                    obj = event.updates[0].object
                    asyncio.create_task(
                        self._check_message(
                            Validator(obj, self.api, self._check, type_message),
                            storage_box
                        )
                    )
            except asyncio.TimeoutError:
                continue
            except Exception as error:
                logger.exception(error)
