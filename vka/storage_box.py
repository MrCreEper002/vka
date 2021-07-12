import dataclasses
from attrdict import AttrDict


@dataclasses.dataclass
class StorageBox:
    commands: AttrDict = dataclasses.field(default_factory=list)
    addition: AttrDict = dataclasses.field(default_factory=AttrDict)
    callback_action: AttrDict = dataclasses.field(default_factory=list)

    def __repr__(self):
        return f'StorageBox({self.commands} {self.addition})'


storage_box = StorageBox()
