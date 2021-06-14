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

from .exception import VkApiError


def random_() -> random:
    return random.getrandbits(31) * random.choice([-1, 1])


def peer_id():
    return 2_000_000_000


def version_api():
    return "5.131"


class API:
    def __init__(
            self,
            token: str,
            version: Union[float, str] = version_api(),
            url: str = "https://api.vk.com/method/",
            lang: int = 0
    ) -> None:
        self._url = url
        self._requests_session = ClientSession()
        self._token = token
        self._method_name = ""
        self._version = version
        self._lang = lang

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
        params['lang'] = self._lang
        resp = await self._requests_session.post(self._url + method_name, data=params)
        response = await resp.json()
        if response.get('error'):
            error = VkApiError(response.get('error'))
            if error.error_code == 6:
                await asyncio.sleep(0.5)
                return await self.method(method_name, params)
            logger.error(error)
            raise error
        return AttrDict(response)

    async def close(self) -> None:
        await self._requests_session.close()
