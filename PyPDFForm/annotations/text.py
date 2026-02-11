# -*- coding: utf-8 -*-
"""
This module defines the `TextAnnotation` class, which is used to represent
a text annotation (sticky note) in a PDF document.

The `TextAnnotation` class encapsulates the properties of a text annotation,
such as its location, dimensions, content, title, and the icon to be displayed.
"""

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import NameObject, TextStringObject

from ..constants import T
from .base import Annotation


@dataclass
class TextAnnotation(Annotation):
    """
    Represents a text annotation in a PDF document.

    This dataclass extends the base `Annotation` class and defines the specific
    attributes and metadata associated with a text annotation, often visualized
    as a sticky note.

    Attributes:
        _annotation_type (str): The PDF internal type of the annotation, which is "/Text".
        note_icon (str): The identifier for a "Note" icon.
        comment_icon (str): The identifier for a "Comment" icon.
        help_icon (str): The identifier for a "Help" icon.
        key_icon (str): The identifier for a "Key" icon.
        insert_icon (str): The identifier for an "Insert" icon.
        title (Optional[str]): The title to be displayed in the annotation's title bar.
        icon (Optional[str]): The name of the icon to be used for the annotation's appearance.
    """

    _annotation_type: str = "/Text"

    note_icon: str = "/Note"
    comment_icon: str = "/Comment"
    help_icon: str = "/Help"
    key_icon: str = "/Key"
    insert_icon: str = "/Insert"

    title: Optional[str] = None
    icon: Optional[str] = None

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the text annotation.

        This method extends the base properties with the title (author)
        and the icon name for the text annotation if they are provided.

        Returns:
            dict: A dictionary of PDF properties specific to the text annotation.
        """
        result = super().get_specific_properties()
        if self.title is not None:
            result[NameObject(T)] = TextStringObject(self.title)
        if self.icon is not None:
            result[NameObject("/Name")] = NameObject(self.icon)

        return result
