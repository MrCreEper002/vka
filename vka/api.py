import asyncio
import enum
import json
import random
import ssl
from typing import Union, Optional, Any
import aiohttp
import certifi
from loguru import logger

from vka.base import AttrDict
from vka.base.exception import VkApiError
from vka.chatbot.registration import Registration

ssl_context = ssl.create_default_context(cafile=certifi.where())


def random_() -> random:
    return random.getrandbits(31) * random.choice([-1, 1])


def version_api():
    return "5.131"


class LANG(enum.Enum):
    """
    LANG.RU.value
    """
    RU: int = 0  # русский
    UK: int = 1  # украинский
    BE: int = 2  # белорусский
    EN: int = 3  # английский
    ES: int = 4  # испанский
    FI: int = 5  # финский
    DE: int = 6  # немецкий
    IT: int = 7  # итальянский


class API:

    """
    Пример использование класса API:

    async def test_api():
        api = API(token='token')
        # сперва нужно создать сессию
        await api.async_init()

        # Есть два варианта обращение к API методам отличие лишь в написание
        # первый вариант
        users_get = await api.method('users.get', {'user_ids': 1})
        # второй вариант
        users_get = api.users.get(user_ids=1)

        # не забываем закрыть сессию
        await api.close()

    asyncio.run(test_api)
    """

    def __init__(
            self,
            *,
            token: str,
            version: Union[float, str] = version_api(),
            url: str = "https://api.vk.com/method/",
            lang: [LANG, int] = LANG.RU.value,
            proxy: str = None,
    ) -> None:
        self._url = url
        self._token = token
        self._method_name = ""
        self._version = version
        self._lang = lang,
        self.proxy = proxy
        self.request: Optional[aiohttp.ClientSession] = None

    async def async_init(self) -> None:
        """ Создание сессии """
        self.request = aiohttp.ClientSession()

    def __getattr__(self, attribute: str):
        if self._method_name:
            self._method_name += f".{attribute}"
        else:
            self._method_name = attribute
        return self

    async def __call__(self, *args, **request_params):
        return await self.method(self._method_name, request_params)

    async def method(self, method_name: str, params: dict):
        """ Обращение к API методу вк """
        self._method_name = ''
        params["access_token"] = self._token
        params["v"] = self._version
        params['lang'] = self._lang
        params = _convert_params_for_api(params)
        response = await self.request.post(
            self._url + method_name,
            data=params,
            proxy=self.proxy,
            ssl=ssl_context
        )
        response = AttrDict((await response.json()))
        match response:
            case {'error': error}:
                error = VkApiError(error)
                if error.error_code == 6:
                    await asyncio.sleep(0.5)
                    return await self.method(method_name, params)
                logger.error(response)
                raise error
            case {'response': _r}:
                return response.response
            case _:
                return response

    async def register(self, user_id) -> Registration:
        return Registration(user_id=user_id, request=self.request)

    async def close(self) -> None:
        await self.request.close()


def _convert_param_value(value: Any, /) -> Any:
    """
    Конвертирует параметр API запроса в соответствии
    с особенностями API и дополнительными удобствами

    value: Текущее значение параметра

    """
    # Для всех перечислений функция вызывается рекурсивно.
    # Массивы в запросе распознаются вк только если записать их как строку,
    # перечисляя значения через запятую
    if isinstance(value, (list, set, tuple)):
        updated_sequence = map(_convert_param_value, value)
        return ",".join(updated_sequence)

    # Все словари, как списки, нужно dumps в JSON
    elif isinstance(value, dict):
        return json.dumps(value)

    # Особенности `aiohttp`
    elif isinstance(value, bool):
        return int(value)

    else:
        return str(value)


def _convert_params_for_api(params: dict, /) -> dict:
    """
    Конвертирует словарь из параметров для метода API,
    учитывая определенные особенности

    params: Параметры, передаваемые для вызова метода API

    вывод:
        Новые параметры, которые можно передать
        в запрос и получить ожидаемый результат

    """
    updated_params = {
        (key[:-1] if key.endswith("_") else key): _convert_param_value(value)
        for key, value in params.items()
        if value is not None
    }
    return updated_params
