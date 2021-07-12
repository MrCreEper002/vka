import asyncio
import json
import random

from attrdict import AttrDict
from typing import Union, Dict
from aiohttp import ClientSession
from loguru import logger

from vka.base.exception import VkApiError


def random_() -> random:
    return random.getrandbits(31) * random.choice([-1, 1])


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

    async def method(self, method_name: str, params: Dict, raw: bool = False, proxy: str = None):
        self._method_name = ''
        params["access_token"] = self._token
        params["v"] = self._version
        params['lang'] = self._lang
        params = _convert_params_for_api(params)
        resp = await self._requests_session.post(self._url + method_name, data=params, proxy=proxy, headers={"user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"})
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


def _convert_param_value(value, /):
    """
    Конвертирует параметр API запроса в соответствии
    с особенностями API и дополнительными удобствами
    Arguments:
        value: Текущее значение параметра
    Returns:
        Новое значение параметра
    """
    # Для всех перечислений функция вызывается рекурсивно.
    # Массивы в запросе распознаются вк только если записать их как строку,
    # перечисляя значения через запятую
    if isinstance(value, (list, set, tuple)):
        updated_sequence = map(_convert_param_value, value)
        return ",".join(updated_sequence)

    # Все словари, как списки, нужно сдампить в JSON
    elif isinstance(value, dict):
        return json.dumps(value)

    # Особенности `aiohttp`
    elif isinstance(value, bool):
        return int(value)

    else:
        return str(value)


def _convert_params_for_api(params: dict, /):
    """
    Конвертирует словарь из параметров для метода API,
    учитывая определенные особенности

    Arguments:
        params: Параметры, передаваемые для вызова метода API

    Returns:
        Новые параметры, которые можно передать
        в запрос и получить ожидаемый результат

    """
    updated_params = {
        (key[:-1] if key.endswith("_") else key): _convert_param_value(value)
        for key, value in params.items()
        if value is not None
    }
    return updated_params
