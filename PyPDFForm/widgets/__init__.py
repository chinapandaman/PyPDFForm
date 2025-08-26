"""
The `widgets` package provides a collection of classes representing various types of PDF form fields (widgets).

It defines `FieldTypes` as a Union of all supported field types, allowing for flexible
type hinting when working with different widget configurations.

Classes within this package encapsulate the properties and behaviors of individual
form fields, facilitating their creation and manipulation within PDF documents.
"""

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
    """
    A container class that provides convenient access to all available PDF form field types.

    This class acts as a namespace for the various `Field` classes defined in the
    `PyPDFForm.widgets` package, making it easier to reference them (e.g., `Fields.TextField`).
    """

    TextField = TextField
    CheckBoxField = CheckBoxField
    RadioGroup = RadioGroup
    DropdownField = DropdownField
    SignatureField = SignatureField
    ImageField = ImageField
