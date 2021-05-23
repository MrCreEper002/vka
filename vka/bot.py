import asyncio
from typing import Iterable

from loguru import logger
from vka.longpoll import LongPoll
from vka.validator import Validator
import inspect


class Bot(LongPoll):
    # def add_command(self, command):
        # logger.debug(inspect.signature(command).parameters)
        # logger.debug(inspect.signature(command).parameters.items())
        # for name, argument in inspect.signature(command).parameters.items():
        #     logger.info(f"{name} {argument.annotation} {argument.annotation is Validator}")
        # self._commands.append(command)

    def run(self, debug: bool = False) -> None:
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._async_run(debug))
            loop.close()
        except KeyboardInterrupt:
            pass

    async def _async_run(self, debug):
        a = (await self.api.method('groups.getById', {})).response[0]
        self.group_id = a.id
        await self._update_long_poll_server()
        logger.success(f"Start LongPollBot -> @club{self.group_id}")

        while True:
            try:
                event = await self._check()
                if debug:
                    logger.debug(event)
                if event.updates:
                    logger.warning(self._storage_box.commands)
                    type_message = event.updates[0].type
                    obj = event.updates[0].object

                    # for cmd in self._commands:
                    #     asyncio.create_task(cmd(type_message, Validator(obj, self.api)))

                    # asyncio.create_task((type_message, Validator(obj, self.api)))

            except Exception as error:
                logger.exception(error)
                # await self._lp_close()
                # return

    def add_command(
            self,
            names: Iterable[str] = (),
            prefixes: Iterable[str] = (),
            any_text: bool = False,):
        pass