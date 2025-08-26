from dataclasses import dataclass
from typing import Union

from .checkbox import CheckBoxField
from .dropdown import DropdownField
from .image import ImageField
from .radio import RadioGroup
from .signature import SignatureField
from .text import TextField

FieldTypes = Union[
    TextField, CheckBoxField, RadioGroup, DropdownField, SignatureField, ImageField
]


@dataclass
class Fields:
    TextField = TextField
    CheckBoxField = CheckBoxField
    RadioGroup = RadioGroup
    DropdownField = DropdownField
    SignatureField = SignatureField
    ImageField = ImageField
