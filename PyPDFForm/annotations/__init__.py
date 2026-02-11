# -*- coding: utf-8 -*-
"""
The `annotations` package provides classes representing various types of PDF annotations.

It defines `AnnotationTypes` as a collection of all supported annotation types, allowing for
flexible type hinting when working with different annotation configurations.

Classes within this package encapsulate the properties and behaviors of individual
annotations, facilitating their creation and manipulation within PDF documents.
"""

from dataclasses import dataclass

from .link import LinkAnnotation
from .text import TextAnnotation
from .text_markup import (HighlightAnnotation, SquigglyAnnotation,
                          StrikeOutAnnotation, UnderlineAnnotation)

AnnotationTypes = (
    TextAnnotation
    | LinkAnnotation
    | HighlightAnnotation
    | UnderlineAnnotation
    | SquigglyAnnotation
    | StrikeOutAnnotation
)


@dataclass
class Annotations:
    """
    A container class that provides convenient access to all available PDF annotation types.

    This class acts as a namespace for the various `Annotation` classes defined in the
    `PyPDFForm.annotations` package, making it easier to reference them (e.g., `Annotations.TextAnnotation`).
    """

    TextAnnotation = TextAnnotation
    LinkAnnotation = LinkAnnotation
    HighlightAnnotation = HighlightAnnotation
    UnderlineAnnotation = UnderlineAnnotation
    SquigglyAnnotation = SquigglyAnnotation
    StrikeOutAnnotation = StrikeOutAnnotation
