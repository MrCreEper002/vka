import asyncio
from vka.api import API, version_api
from loguru import logger
from vka.base import AttrDict
from vka.base.wrapper import EventBase


class LongPoll:
    """
    ЛонгПул который получает сообщения присылаемые пользователями боту
    """

    def __init__(
            self, token: str, debug: bool = False,
            wait: int = 25, lang: int = 0, version: str = version_api()
    ):
        self._token = token
        self._lang = lang
        self._version = version
        self._wait = wait
        self.api = API(token=self._token, lang=self._lang, version=self._version)
        self.group_id = None
        self.debug = debug

    async def _init(self):
        await self.api.init()
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
        res = await self.api._requests_session.post(
            url=self._url, data=data, timeout=self._wait+10
        )
        response = AttrDict(await res.json())

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
        return []

    async def _listen(self):
        try:
            logger.success(f"Запуск бота в группе -> @club{self.group_id}")
            while True:
                try:
                    yield await self._check()
                except asyncio.TimeoutError:
                    continue
                except Exception as vka_error:
                    logger.error(vka_error)
                    continue
        finally:
            logger.success(f"Остановка бота -> @club{self.group_id}")
            await self._lp_close()
            return

    async def _lp_close(self):
        await self.api.close()

