# -*- coding: utf-8 -*-

from dataclasses import dataclass

from pypdf.generic import ArrayObject, FloatObject, NameObject

from .base import Annotation


@dataclass
class TextMarkupAnnotation(Annotation):
    def get_specific_properties(self) -> dict:
        return {
            NameObject("/QuadPoints"): ArrayObject(
                [
                    FloatObject(self.x),
                    FloatObject(self.y),
                    FloatObject(self.x + self.width),
                    FloatObject(self.y),
                    FloatObject(self.x),
                    FloatObject(self.y + self.height),
                    FloatObject(self.x + self.width),
                    FloatObject(self.y + self.height),
                ]
            )
        }


@dataclass
class HighlightAnnotation(TextMarkupAnnotation):
    _annotation_type: str = "/Highlight"


@dataclass
class UnderlineAnnotation(TextMarkupAnnotation):
    _annotation_type: str = "/Underline"


@dataclass
class SquigglyAnnotation(TextMarkupAnnotation):
    _annotation_type: str = "/Squiggly"


@dataclass
class StrikeOutAnnotation(TextMarkupAnnotation):
    _annotation_type: str = "/StrikeOut"
