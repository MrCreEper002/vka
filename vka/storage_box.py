import dataclasses
from attrdict import AttrDict


@dataclasses.dataclass
class StorageBox:
    commands: list = dataclasses.field(default_factory=list)
    addition: AttrDict = dataclasses.field(default_factory=AttrDict)
    callback_action: dict = dataclasses.field(default_factory=dict)
    messages_ids: dict = dataclasses.field(default_factory=dict)

    def __repr__(self):
        return f'StorageBox({self.commands} {self.addition})'


storage_box = StorageBox()
