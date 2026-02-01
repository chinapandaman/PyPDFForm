# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import NameObject, TextStringObject

from ..constants import T
from .base import Annotation


@dataclass
class TextAnnotation(Annotation):
    _annotation_type: str = "/Text"
    _additional_properties: tuple = (
        (NameObject(T), (TextStringObject, "title")),
        (NameObject("/Name"), (NameObject, "icon")),
    )

    note_icon: str = "/Note"
    comment_icon: str = "/Comment"

    title: Optional[str] = None
    icon: Optional[str] = None
