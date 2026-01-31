# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Union

from .text import TextAnnotation

AnnotationTypes = Union[TextAnnotation]


@dataclass
class Annotations:
    TextAnnotation = TextAnnotation
