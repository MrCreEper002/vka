import asyncio
import enum
import json
import re
import time
import urllib.parse
import random

from attrdict import AttrDict
from typing import Optional, Union, Dict
from aiohttp import ClientSession
from loguru import logger


def random_() -> random:
    return random.getrandbits(31) * random.choice([-1, 1])


def peer_id():
    return 2_000_000_000


class VkApiError(Exception):
    def __init__(self, resp: AttrDict):
        self._resp = AttrDict(resp)
        self.error_code = self._resp.error_code
        self.error_msg = self._resp.error_msg
        self._msg = f'[{self.error_code}] {self.error_msg}'
        logger.error(self._msg)

    def __str__(self):
        return self._msg

    def __call__(self, *args, **kwargs):
        return self._msg


class API:

    RPS_DELAY = 0.34

    def __init__(
            self,
            token: str,
            version: Union[float, str] = "5.135",
            url: str = "https://api.vk.com/method/",
    ) -> None:
        self._url = url
        self._requests_session = ClientSession()
        self._token = token
        self._method_name = ""
        self._version = version

    def __getattr__(self, attribute: str):
        if self._method_name:
            self._method_name += f".{attribute}"
        else:
            self._method_name = attribute
        return self

    async def __call__(self, *args, **request_params):
        return await self.method(self._method_name, request_params)

    async def method(self, method_name: str, params: Dict, raw: bool = False):
        self._method_name = ''
        params["access_token"] = self._token
        params["v"] = self._version
        resp = await self._requests_session.post(self._url + method_name, data=params)
        response = await resp.json()
        if response.get('error'):
            error = VkApiError(response.get('error'))
            if error.error_code == 6:
                await asyncio.sleep(0.5)
                return await self.method(method_name, params)
            return error
        return AttrDict(response)

    async def close(self) -> None:
        await self._requests_session.close()
