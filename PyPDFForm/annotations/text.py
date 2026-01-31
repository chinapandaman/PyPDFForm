# -*- coding: utf-8 -*-

from dataclasses import dataclass

from pypdf.generic import NameObject

from .base import Annotation


@dataclass
class TextAnnotationIcons:
    comment = "/Comment"


@dataclass
class TextAnnotation(Annotation):
    _annotation_type: str = "/Text"

    icon: str = "/Comment"

    _additional_properties: tuple = (
        (NameObject("/Name"), NameObject(icon)),
    )
