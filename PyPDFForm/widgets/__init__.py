from dataclasses import dataclass
from typing import Union

from .checkbox import CheckBoxField
from .radio import RadioField
from .text import TextField

FieldTypes = Union[TextField, CheckBoxField, RadioField]


@dataclass
class Fields:
    TextField = TextField
    CheckBoxField = CheckBoxField
    RadioField = RadioField
