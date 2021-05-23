import datetime
import json
from typing import Optional, List

from attrdict import AttrDict

from vka.api import peer_id
from vka.base.wrapper import Wrapper


class Message(Wrapper):

    @property
    def id(self) -> int:
        return self.fields.message.id

    @property
    def peer_id(self) -> int:
        return self.fields.message.peer_id

    @property
    def chat_id(self) -> int:
        chat_id = self.message.peer_id - peer_id()
        if chat_id < 0:
            raise ValueError(
                "Can't get `chat_id` if message wasn't sent in a chat"
            )

        return chat_id

    @property
    def conversation_message_id(self) -> int:
        return self.fields.message.conversation_message_id

    @property
    def date(self) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(self.fields.message.date)

    @property
    def from_id(self) -> int:
        return self.fields.message.from_id

    @property
    def text(self) -> str:
        return self.fields.message.text

    @property
    def random_id(self) -> int:
        return self.fields.message.random_id

    @property
    def attachments(self) -> List[AttrDict]:
        return list(self.fields.message.attachments)

    @property
    def important(self) -> bool:
        return bool(self.fields.message.important)

    @property
    def is_hidden(self) -> bool:
        return bool(self.fields.message.important)

    @property
    def out(self) -> bool:
        return bool(self.fields.message.out)

    @property
    def keyboard(self) -> Optional[AttrDict]:
        if "keyboard" in self.fields:
            return AttrDict(json.loads(self.fields.message.keyboard))
        return None

    @property
    def fwd_messages(self):
        return list(map(self.__class__, self.fields.message.fwd_messages))

    @property
    def payload(self) -> Optional[AttrDict]:
        if "payload" in self.fields:
            return AttrDict(json.loads(self.fields.message.payload))
        return None

    @property
    def reply_message(self):
        if "reply_message" in self.fields:
            return self.__class__(self.fields.message.reply_message)
        return None

    @property
    def action(self) -> Optional[AttrDict]:
        return self.fields.message.action if "action" in self.fields else None



