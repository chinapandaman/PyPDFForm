# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Union

from .text import RawText

RawTypes = Union[RawText]


@dataclass
class RawElements:
    Text = RawText
