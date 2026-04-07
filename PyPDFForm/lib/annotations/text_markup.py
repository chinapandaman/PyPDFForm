# -*- coding: utf-8 -*-
"""
This module defines the `TextMarkupAnnotation` class and its subclasses,
which are used to represent text markup annotations in a PDF document.

Classes:
    - `TextMarkupAnnotation`: Base class for all text markup annotations.
    - `HighlightAnnotation`: Represents a highlight annotation.
    - `UnderlineAnnotation`: Represents an underline annotation.
    - `SquigglyAnnotation`: Represents a squiggly (curly) underline annotation.
    - `StrikeOutAnnotation`: Represents a strikeout annotation.
"""

from dataclasses import dataclass

from pypdf.generic import ArrayObject, FloatObject, NameObject

from .base import Annotation


@dataclass
class TextMarkupAnnotation(Annotation):
    """
    Base dataclass for all text markup annotations.

    Text markup annotations appear as marks on the text of a document,
    such as highlights, underlines, etc. They are defined by a set of
    quadrilateral points (QuadPoints) that encompass the text being marked.
    """

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the text markup annotation.

        This method extends the base properties with the `QuadPoints` for
        the markup based on the annotation's position and dimensions.

        Returns:
            dict: A dictionary of PDF properties specific to the text markup annotation.
        """
        result = super().get_specific_properties()
        result.update(
            {
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
                ),
            }
        )

        return result


@dataclass
class HighlightAnnotation(TextMarkupAnnotation):
    """Represents a highlight annotation."""

    _annotation_type: str = "/Highlight"


@dataclass
class UnderlineAnnotation(TextMarkupAnnotation):
    """Represents an underline annotation."""

    _annotation_type: str = "/Underline"


@dataclass
class SquigglyAnnotation(TextMarkupAnnotation):
    """Represents a squiggly (curly) underline annotation."""

    _annotation_type: str = "/Squiggly"


@dataclass
class StrikeOutAnnotation(TextMarkupAnnotation):
    """Represents a strikeout annotation."""

    _annotation_type: str = "/StrikeOut"
