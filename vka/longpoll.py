import asyncio
from attrdict import AttrDict

from vka.base.message import Message
from vka.storage_box import storage_box
from .api import API
from aiohttp import ClientSession
from loguru import logger


class LongPoll:
    def __init__(self, token: str, wait: int = 25):
        self._commands = []
        self._session = ClientSession()
        self._token = token
        self._wait = wait
        self.api = API(self._token)
        self.group_id = 0
        self._storage_box = storage_box

    async def _update_long_poll_server(self, ts: bool = True):
        long_poll = await self.api.groups.getLongPollServer(group_id=self.group_id)
        res = AttrDict(long_poll)
        self._key = res.response.key
        if ts:
            self._ts = res.response.ts
        self._url = res.response.server

    async def _check(self):
        data = {
            'act': 'a_check',
            'key': self._key,
            'ts': self._ts,
            'wait': self._wait,
        }
        res = await self._session.post(url=self._url, data=data, timeout=self._wait)
        response = AttrDict(await res.json())
        if 'failed' not in response:
            self._ts = response.ts
            return response
        elif response.failed == 2:
            await self._update_long_poll_server(False)
        elif response.failed == 3:
            await self._update_long_poll_server()
        return await self._check()

    async def _lp_close(self):
        await self.api.close()
        await self._session.close()



