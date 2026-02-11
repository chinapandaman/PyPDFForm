# -*- coding: utf-8 -*-
"""
This module defines the class for link annotations in PyPDFForm.

It provides a structure for representing and interacting with PDF link
annotations, which allow users to click and navigate to a URI.

Classes:
    - `LinkAnnotation`: A dataclass representing the properties of a PDF link annotation.
"""

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import DictionaryObject, NameObject, TextStringObject

from ..constants import A, S
from .base import Annotation


@dataclass
class LinkAnnotation(Annotation):
    """
    A dataclass representing the properties of a PDF link annotation.

    This class extends the `Annotation` base class to specifically handle
    link annotations, including the target URI.

    Attributes:
        uri (str): The URI that the link annotation points to. Defaults to None.
    """

    _annotation_type: str = "/Link"

    uri: Optional[str] = None

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the link annotation type.

        This method returns a dictionary containing PDF properties and their
        values that are unique to a link annotation, perforated with the URI action.

        Returns:
            dict: A dictionary of PDF properties specific to the link annotation.
        """
        result = {}
        if self.uri is not None:
            result[NameObject(A)] = DictionaryObject(
                {
                    NameObject(S): NameObject("/URI"),
                    NameObject("/URI"): TextStringObject(self.uri),
                }
            )

        return result
