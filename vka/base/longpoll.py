from attrdict import AttrDict
from vka.storage_box import storage_box
from vka.api import API, version_api
from aiohttp import ClientSession
from loguru import logger


class LongPoll:
    """
    главный класс отвечающий за лонгпул
    """
    def __init__(self, token: str, wait: int = 25, lang: int = 0, version: str = version_api()):
        self._commands = []
        self._session = ClientSession()
        self._token = token
        self._wait = wait
        self.api = API(self._token, lang=lang, version=version)
        self.group_id = 0
        self._storage_box = storage_box
        self._state = {}
        self._debug = False

    def _get(self):
        logger.info(self._state)

    def __setitem__(self, key, value):
        self._state[key] = value

    def __getitem__(self, key):
        return self._state[key]

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



