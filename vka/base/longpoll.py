import asyncio
from traceback import format_exc
from typing import Optional
import aiohttp
from vka.api import version_api, API, ssl_context
from loguru import logger
from vka.base import AttrDict
from vka.base.wrapper import EventBase
from vka.chatbot import KeyAndBoxStorage


class LongPoll(KeyAndBoxStorage):
    """
    LongPoll
    """

    def __init__(
            self, token: str,
            wait: int = 25, lang: int = 0,
            version: str = version_api(),
    ):
        KeyAndBoxStorage.__init__(self)
        self.token = token
        self.lang = lang
        self.version = version
        self._wait = wait
        self.api: Optional[API] = None
        self.group_id = None
        self.request: Optional[aiohttp.ClientSession] = None

    async def async_init(self):
        self.request = aiohttp.ClientSession()
        self.api = API(token=self.token)
        await self.api.async_init()
        self.group_id = (
            await self.api.method('groups.getById', {})
        )[0].id
        await self._update_long_poll_server()

    async def _update_long_poll_server(self, ts: bool = True):
        long_poll = await self.api.groups.getLongPollServer(group_id=self.group_id)
        self._key = long_poll.key
        if ts:
            self._ts = long_poll.ts
        self._url = long_poll.server

    async def _check(self):
        data = {
            'act': 'a_check',
            'key': self._key,
            'ts': self._ts,
            'wait': self._wait,
        }
        response = await self.request.post(
            url=self._url, data=data, timeout=self._wait+10, ssl=ssl_context
        )
        response = AttrDict(await response.json())
        match response:
            case {'failed': failed} if failed == 1:
                self._ts = response.ts
            case {'failed': failed} if failed == 2:
                await self._update_long_poll_server(False)
            case {'failed': failed} if failed == 3:
                await self._update_long_poll_server()
            case _:
                self._ts = response.ts
                return EventBase(response)
        return await self._check()

    async def listen(self):
        try:
            logger.success(f"[vka] Запуск бота в группе -> @club{self.group_id}")
            while True:
                try:
                    yield await self._check()
                except asyncio.TimeoutError:
                    continue
                except Exception as vka_error:
                    logger.error(format_exc())
                    if str(vka_error) in 'Session is closed':
                        logger.success(f"[vka] Аварийная остановка бота -> @club{self.group_id}")
                        await self._lp_close()
                        return
                    await asyncio.sleep(1)
                    continue
        finally:
            logger.success(f"[vka] Остановка бота -> @club{self.group_id}")
            await self._lp_close()
            return

    async def _lp_close(self):
        await self.api.request.close()
        await self.request.close()
        if self.__state__.get('run_custom_func') is not None:
            self.get_item(key='run_custom_func').cancel()
        self.__state__.clear()
        self.__message_ids__.clear()
        self.__commands__.clear()
        self.__addition__.clear()
        self.__menu_commands__.clear()
        self.__callback_action__.clear()

