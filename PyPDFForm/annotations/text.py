# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import NameObject, TextStringObject

from ..constants import T
from .base import Annotation


@dataclass
class TextAnnotation(Annotation):
    _annotation_type: str = "/Text"

    comment_icon: str = "/Comment"
    note_icon: str = "/Note"

    title: Optional[str] = None
    icon: Optional[str] = comment_icon

    _additional_properties: tuple = (
        (NameObject(T), (TextStringObject, "title")),
        (NameObject("/Name"), (NameObject, "icon")),
    )
