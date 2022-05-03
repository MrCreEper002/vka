import ssl
import aiohttp
import typing


class SessionContainerMixin:

    def __init__(
            self,
            *,
            requests_session: typing.Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """
        requests_session: Кастомная `aiohttp`-сессия для HTTP запросов.
        """
        self.__session = requests_session

    @property
    def requests_session(self) -> aiohttp.ClientSession:
        """
        Возвращает сессию, которую можно использовать для
        отправки запросов. Если сессия еще не была создана,
        произойдет инициализация. Не рекомендуется использовать
        этот проперти вне корутин.
        """
        if self.__session is None or self.__session.closed:
            self.__session = self._init_aiohttp_session()

        return self.__session

    async def __aenter__(self) -> "SessionContainerMixin":
        """
        Позволяет автоматически закрыть сессию
        запросов по выходу из `async with` блока.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close_session()

    async def close_session(self) -> None:
        """
        Закрывает используемую `aiohttp` сессию.
        Можно использовать асинхронный менеджер контекста
        вместо этого метода.
        """
        if self.__session is not None:
            await self.__session.close()

    @staticmethod
    def _init_aiohttp_session() -> aiohttp.ClientSession:
        """
        Инициализирует `aiohttp`-сессию.
        Returns:
            Новая `aiohttp`-сессия
        """
        return aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl.SSLContext()),
            skip_auto_headers={"User-Agent"},
            raise_for_status=True,
        )
