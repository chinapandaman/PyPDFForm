# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Union

from .image import RawImage
from .text import RawText

RawTypes = Union[RawText, RawImage]


@dataclass
class RawElements:
    RawText = RawText
    RawImage = RawImage
