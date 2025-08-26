from dataclasses import dataclass
from typing import Union

from .checkbox import CheckBoxField
from .dropdown import DropdownField
from .image import ImageField
from .radio import RadioField
from .signature import SignatureField
from .text import TextField

FieldTypes = Union[
    TextField, CheckBoxField, RadioField, DropdownField, SignatureField, ImageField
]


@dataclass
class Fields:
    TextField = TextField
    CheckBoxField = CheckBoxField
    RadioField = RadioField
    DropdownField = DropdownField
    SignatureField = SignatureField
    ImageField = ImageField
