import asyncio
import inspect
from typing import Iterable

from loguru import logger

from vka.storage_box import storage_box
from vka.validator import Validator


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
            type_message: str,
            ctx: Validator,
            storage: storage_box
    ):
        for command in storage.commands:
            if command['any_text']:
                # await self.init_func(command['func_obj'])
                asyncio.create_task(command['func_obj'](type_message, ctx))
                continue
            if command['names'] == ctx.msg.text:
                # await self.init_func(command['func_obj'])
                asyncio.create_task(command['func_obj'](type_message, ctx))


    async def init_func(self, func):

        for name, argument in inspect.signature(func).parameters.items():
            if argument.annotation is Validator:
                print(argument, 1)
            else:
                print(argument, 2)
            # logger.info(f"{name} {argument.annotation} {argument.annotation is Validator}")


# CommandsTest = Commands()
