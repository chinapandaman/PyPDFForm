# -*- coding: utf-8 -*-

from dataclasses import dataclass


@dataclass
class Annotation:
    page_number: int
    x: float
    y: float
    width: float = 20
    height: float = 20
    contents: str = ""
