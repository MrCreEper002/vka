from attrdict import AttrDict
from vka.storage_box import storage_box
from loguru import logger


class Wrapper:

    def __init__(self, fields: AttrDict):
        if isinstance(fields, dict):
            fields = AttrDict(fields)
        self._fields = fields

    @property
    def fields(self):
        return self._fields
