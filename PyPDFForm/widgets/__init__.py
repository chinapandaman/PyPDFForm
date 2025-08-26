from dataclasses import dataclass
from typing import Union

from .checkbox import CheckBoxField
from .dropdown import DropdownField
from .radio import RadioField
from .text import TextField

FieldTypes = Union[TextField, CheckBoxField, RadioField, DropdownField]


@dataclass
class Fields:
    TextField = TextField
    CheckBoxField = CheckBoxField
    RadioField = RadioField
    DropdownField = DropdownField
