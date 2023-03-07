import datetime
import json
import typing

from vka.base.attrdict import AttrDict
# from vka.base.wrapper import Event


def peer_id():
    return 2_000_000_000


class Message:

    def __init__(self, message):
        self.message = message

    @property
    def date(self) -> datetime:
        """ Время отправки сообщения """
        return datetime.datetime.fromtimestamp(self.message.date)

    @property
    def from_id(self) -> int:
        """ Идентификатор отправителя """
        return self.message.from_id

    @property
    def id(self) -> int:
        """ Идентификатор сообщения """
        return self.message.id

    @property
    def peer_id(self) -> int:
        """ Идентификатор назначения """
        return self.message.peer_id

    @property
    def text(self) -> str:
        """ Текст сообщения """
        return self.message.text

    @property
    def conversation_message_id(self) -> int:
        """ Уникальный автоматически увеличивающийся номер для всех сообщений с этим peer """
        return self.message.conversation_message_id

    @property
    def fwd_messages(self) -> list:
        """
            Массив пересланных сообщений (если есть).
            Максимальное количество элементов — 100.
            Максимальная глубина вложенности для пересланных сообщений — 45,
            общее максимальное количество в цепочке с учетом вложенности — 500.
        """
        return self.message.fwd_messages

    @property
    def important(self) -> bool:
        """ Сообщение помеченное как важное """
        return bool(self.message.important)

    @property
    def random_id(self) -> int:
        """
            Идентификатор, используемый при отправке сообщения.
            Возвращается только для исходящих сообщений
        """
        return self.message.random_id

    @property
    def attachments(self) -> list:
        """ Медиа-вложения сообщения (фотографии, ссылки и т.п.).  """
        return self.message.attachments

    @property
    def reply_message(self) -> AttrDict:
        """ Сообщение, в ответ на которое отправлено текущее """
        return self.message.reply_message

    @property
    def action(self) -> list:
        """ Информация о сервисном действии с чатом """
        return self.message.action

    @property
    def payload(self) -> AttrDict | None:
        """ Сервисное поле для сообщений ботам (полезная нагрузка) """
        if "payload" in self.message:
            return AttrDict(json.loads(self.message.payload))
        return None

    @property
    def is_hidden(self) -> bool:
        return bool(self.message.is_hidden)

    @property
    def chat_id(self) -> int:
        """ Идентификатор беседы """
        chat_id = self.peer_id - peer_id()
        if chat_id < 0:
            raise ValueError(
                "Can't get `chat_id` if message wasn't sent in a chat"
            )

        return chat_id

    @property
    def ref(self) -> typing.Any:
        """ Произвольный параметр для работы """
        return self.message.ref

    @property
    def ref_source(self) -> typing.Any:
        """ Произвольный параметр для работы """
        return self.message.ref_source
