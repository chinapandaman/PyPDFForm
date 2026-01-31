# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

from pypdf.generic import NameObject

from .base import Annotation


class TextAnnotationIcons(Enum):
    comment: str = "/Comment"


@dataclass
class TextAnnotation(Annotation):
    _annotation_type: str = "/Text"

    icons = TextAnnotationIcons
    icon = icons.comment

    _additional_properties: tuple = ((NameObject("/Name"), NameObject(icon.value)),)
