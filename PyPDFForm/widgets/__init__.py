from dataclasses import dataclass
from typing import Union

from .checkbox import CheckBoxField
from .text import TextField

FieldTypes = Union[TextField, CheckBoxField]


@dataclass
class Fields:
    TextField = TextField
    CheckBoxField = CheckBoxField
