from dataclasses import dataclass
from typing import Union

from .text import TextField

FieldTypes = Union[TextField]


@dataclass
class Fields:
    TextField = TextField
