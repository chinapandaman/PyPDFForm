# -*- coding: utf-8 -*-

from dataclasses import dataclass

from .checkbox import Checkbox
from .dropdown import Dropdown
from .image import Image
from .radio import Radio
from .signature import Signature
from .text import Text


@dataclass
class Widgets:
    Text = Text
    Checkbox = Checkbox
    Radio = Radio
    Dropdown = Dropdown
    Signature = Signature
    Image = Image
