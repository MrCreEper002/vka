from attrdict import AttrDict
from vka.storage_box import storage_box


class Wrapper:

    def __init__(self, fields: AttrDict):
        if isinstance(fields, dict):
            fields = AttrDict(fields)
        self._fields = fields

    @property
    def fields(self):
        return self._fields

    @property
    def storage_box(self):
        return storage_box
