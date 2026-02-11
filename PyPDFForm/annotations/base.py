# -*- coding: utf-8 -*-
"""
This module defines the base class for all annotations in PyPDFForm.

It provides a foundational structure for representing and interacting with
different types of PDF annotations, such as text annotations.

Classes:
    - `Annotation`: A dataclass representing the common properties of a PDF annotation.
"""

from dataclasses import dataclass

from pypdf.generic import (ArrayObject, DictionaryObject, FloatObject,
                           NameObject, TextStringObject)

from ..constants import Annot, Contents, Rect, Subtype, Type


@dataclass
class Annotation:
    """
    Base dataclass for all PDF annotations.

    This class defines the common properties that all types of annotations
    (e.g., text annotations) share. Specific annotation types will extend this
    class to add their unique attributes.

    Attributes:
        page_number (int): The 1-based page number on which the annotation is located.
        x (float): The x-coordinate of the annotation's position on the page.
        y (float): The y-coordinate of the annotation's position on the page.
        width (float): The width of the annotation. Defaults to 20.
        height (float): The height of the annotation. Defaults to 20.
        contents (str): The contents of the annotation. Defaults to "".
    """

    page_number: int
    x: float
    y: float
    width: float = 20
    height: float = 20
    contents: str = ""

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the annotation type.

        This method constructs the base dictionary containing PDF properties
        and their values that are common to all types of annotations.
        These properties are used when creating the annotation's entry in
        the PDF document.

        Returns:
            dict: A dictionary of PDF properties specific to the annotation type.
        """
        return DictionaryObject(
            {
                NameObject(Type): NameObject(Annot),
                NameObject(Subtype): NameObject(getattr(self, "_annotation_type")),
                NameObject(Rect): ArrayObject(
                    [
                        FloatObject(self.x),
                        FloatObject(self.y),
                        FloatObject(self.x + self.width),
                        FloatObject(self.y + self.height),
                    ]
                ),
                NameObject(Contents): TextStringObject(self.contents),
            }
        )
