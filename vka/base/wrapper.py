import typing
import datetime
from vka.base.attrdict import AttrDict


def peer_id():
    return 2_000_000_000


class EventBase:
    def __init__(self, event):
        self._event = event
        self._ts: str = event.ts
        self._updates: list = event.updates

    @property
    def ts(self) -> str:
        return self._ts

    @property
    def updates(self) -> list['Event']:
        return self._updates

    def __repr__(self):
        return f"{self._event}"


class Event:
    def __init__(self, event):
        self._event = event

    @property
    def type(self) -> str:
        return self._event.type

    @property
    def obj(self) -> AttrDict:
        return self._event.object

    @property
    def message(self) -> "Message":
        return self.obj.message

    @property
    def group_id(self) -> int:
        return self._event.group_id

    @property
    def event_id(self) -> str:
        return self._event.event_id

    def __repr__(self):
        return f'{self._event}'


class Wrapper(dict):

    def __init__(self, fields: AttrDict):
        super().__init__()
        if isinstance(fields, dict):
            fields = AttrDict(fields)
        self._fields = fields

    @property
    def fields(self):
        if 'message' in self._fields:
            return self._fields.message
        return self._fields


class Message(Wrapper):

    @property
    def date(self) -> datetime:
        """ Время отправки сообщения """
        return datetime.datetime.fromtimestamp(self.fields.date)

    @property
    def from_id(self) -> int:
        """ Идентификатор отправителя """
        try:
            return self.fields.from_id
        except AttributeError:
            return self.fields.user_id

    @property
    def id(self) -> int:
        """ Идентификатор сообщения """
        return self.fields.id

    @property
    def peer_id(self) -> int:
        """ Идентификатор назначения """
        return self.fields.peer_id

    @property
    def text(self) -> str:
        """ Текст сообщения """
        return self.fields.text

    @property
    def conversation_message_id(self) -> int:
        """ Уникальный автоматически увеличивающийся номер для всех сообщений с этим peer """
        return self.fields.conversation_message_id

    @property
    def fwd_messages(self) -> list:
        """
            Массив пересланных сообщений (если есть).
            Максимальное количество элементов — 100.
            Максимальная глубина вложенности для пересланных сообщений — 45,
            общее максимальное количество в цепочке с учетом вложенности — 500.
        """
        return self.fields.fwd_messages

    @property
    def important(self) -> bool:
        """ Сообщение помеченное как важное """
        return bool(self.fields.important)

    @property
    def random_id(self) -> int:
        """
            Идентификатор, используемый при отправке сообщения.
            Возвращается только для исходящих сообщений
        """
        return self.fields.random_id

    @property
    def attachments(self) -> list:
        """ Медиа-вложения сообщения (фотографии, ссылки и т.п.).  """
        return self.fields.attachments

    @property
    def reply_message(self) -> ['Message', None]:
        """ Сообщение, в ответ на которое отправлено текущее """
        if "reply_message" in self.fields:
            return self.__class__(self.fields.reply_message)
        return None

    @property
    def action(self) -> AttrDict:
        """ Информация о сервисном действии с чатом """
        return AttrDict(self.fields.action)

    @property
    def payload(self) -> AttrDict | None:
        """ Сервисное поле для сообщений ботам (полезная нагрузка) """
        if "payload" in self.fields:
            return AttrDict(self.fields.payload)
        return None

    @property
    def is_hidden(self) -> bool:
        return bool(self.fields.is_hidden)

    @property
    def chat_id(self) -> int | bool:
        """ Идентификатор беседы """
        chat_id = self.peer_id - peer_id()
        if chat_id < 0:
            return False
        return chat_id

    @property
    def ref(self) -> typing.Any:
        """ Произвольный параметр для работы """
        return self.fields.ref

    @property
    def ref_source(self) -> typing.Any:
        """ Произвольный параметр для работы """
        return self.fields.ref_source

    def __repr__(self):
        return f"{self.fields}"
