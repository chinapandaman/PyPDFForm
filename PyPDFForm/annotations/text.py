# -*- coding: utf-8 -*-

from dataclasses import dataclass

from pypdf.generic import NameObject

from .base import Annotation


@dataclass
class TextAnnotation(Annotation):
    _annotation_type: str = "/Text"

    comment_icon: str = "/Comment"

    icon: str = comment_icon

    _additional_properties: tuple = ((NameObject("/Name"), NameObject(icon)),)
