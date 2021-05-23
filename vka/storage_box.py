import dataclasses
from typing import List

from attrdict import AttrDict


@dataclasses.dataclass
class StorageBox:
    commands: AttrDict = dataclasses.field(default_factory=list)
    addition: AttrDict = dataclasses.field(default_factory=AttrDict)

    def __repr__(self):
        return f'<Commands={len(self.commands)}>'


class Attr(dict):
    def __init__(self, *args, **kwargs):
        super(Attr, self).__init__(*args, **kwargs)
        self.__dict__ = self


storage_box = StorageBox()
