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

        public_access = s.find('ya:publicaccess').text \
            if s.find('ya:publicaccess') is not None else None

        profile_state = s.find('ya:profilestate').text \
            if s.find('ya:profilestate') is not None else None

        user_id = s.find('ya:uri').attrs.get('rdf:resource') \
            if s.find('ya:uri') is not None else None

        first_name = s.find('ya:firstname').text \
            if s.find('ya:firstname') is not None else None

        second_name = s.find('ya:secondname').text \
            if s.find('ya:secondname') is not None else None

        gender = s.find('foaf:gender').text \
            if s.find('foaf:gender') is not None else None

        subscribers_count = s.find('ya:subscriberscount').text \
            if s.find('ya:subscriberscount') is not None else None

        friends_count = s.find('ya:friendscount').text \
            if s.find('ya:friendscount') is not None else None

        subscribed_to_count = s.find('ya:subscribedtocount').text \
            if s.find('ya:subscribedtocount') is not None else None

        birthday = s.find('foaf:birthday').text \
            if s.find('foaf:birthday') is not None else None

        return {
            "public_access": public_access,
            "profile_state": profile_state,
            "id": user_id,
            "first_name": first_name,
            "second_name": second_name,
            "name": f"{first_name} {second_name}",
            "gender": gender,
            "subscribers_count": subscribers_count,
            "friends_count": friends_count,
            "subscribed_to_count": subscribed_to_count,
            "birthday": birthday,
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
