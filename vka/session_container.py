import ssl
import aiohttp


class SessionContainerMixin:

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
