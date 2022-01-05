from aiohttp import ClientSession
from bs4 import BeautifulSoup


class Registration:
    """
    Чтобы получить дату когда зарегистрирован пользователь
    """

    def __init__(
            self,
            user_id: int,
            url: str = 'https://vk.com/foaf.php?id='
    ):
        self._url = url + str(user_id)
        self._requests_session = ClientSession()
        self.user_id = user_id

    async def get_date(self) -> BeautifulSoup:
        response = await self._requests_session.get(url=self._url)
        await self._requests_session.close()
        soup = BeautifulSoup(await response.text(), 'html.parser')
        return soup
