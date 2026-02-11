# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import DictionaryObject, NameObject, TextStringObject

from ..constants import A, S
from .base import Annotation


@dataclass
class LinkAnnotation(Annotation):
    _annotation_type: str = "/Link"

    uri: Optional[str] = None

    def get_specific_properties(self) -> dict:
        result = {}
        if self.uri is not None:
            result[NameObject(A)] = DictionaryObject(
                {
                    NameObject(S): NameObject("/URI"),
                    NameObject("/URI"): TextStringObject(self.uri),
                }
            )

        return result
