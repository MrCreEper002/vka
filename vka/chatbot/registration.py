import ssl
from datetime import datetime
import certifi
from aiohttp import ClientSession
from bs4 import BeautifulSoup

ssl_context = ssl.create_default_context(cafile=certifi.where())


class Registration:
    """
    Чтобы получить дату когда зарегистрирован пользователь
    """

    def __init__(
            self,
            user_id: int,
            request: ClientSession,
            url: str = 'https://vk.com/foaf.php?id=',
    ):
        self._url = url + str(user_id)
        self.request = request
        self.user_id = user_id

    async def soup(self) -> BeautifulSoup:
        response = await self.request.get(
            url=self._url, ssl=ssl_context
        )
        soup = BeautifulSoup(await response.text(), 'html.parser')
        return soup

    async def get_obj(self):
        s = await self.soup()

        last_logged_in = datetime.strptime(
            s.find('ya:lastloggedin').attrs.get('dc:date'),
            "%Y-%m-%dT%H:%M:%S+03:00"
        ) if s.find('ya:lastloggedin') is not None \
            else s.find('ya:lastloggedin')
        location = s.find('ya:location').attrs.get('ya:city') \
            if s.find('ya:location') is not None \
            else s.find('ya:location')

        return {
            "public_access": s.find('ya:publicaccess').text,
            "profile_state": s.find('ya:profilestate').text,
            "id": s.find('ya:uri').attrs.get('rdf:resource'),
            "first_name": s.find('ya:firstname').text,
            "second_name": s.find('ya:secondname').text,
            "name": s.find('foaf:name').text,
            "gender": s.find('foaf:gender').text,
            "subscribers_count": s.find('ya:subscriberscount').text,
            "friends_count": s.find('ya:friendscount').text,
            "subscribed_to_count": s.find('ya:subscribedtocount').text,
            "birthday": s.find('foaf:birthday').text,
            "location": location,
            "created": datetime.strptime(
                s.find('ya:created').attrs.get('dc:date'),
                "%Y-%m-%dT%H:%M:%S+03:00"
            ),
            "modified": datetime.strptime(
                s.find('ya:modified').attrs.get('dc:date'),
                "%Y-%m-%dT%H:%M:%S+03:00"
            ),
            "last_logged_in": last_logged_in,
        }
