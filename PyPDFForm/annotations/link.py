# -*- coding: utf-8 -*-
# TODO: finish other features
"""
This module defines the class for link annotations in PyPDFForm.

It provides a structure for representing and interacting with PDF link
annotations, which allow users to click and navigate to a URI or an internal page.

Classes:
    - `LinkAnnotation`: A dataclass representing the properties of a PDF link annotation.
"""

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import (ArrayObject, DictionaryObject, NameObject,
                           NumberObject, TextStringObject)

from ..constants import A, S
from .base import Annotation


@dataclass
class LinkAnnotation(Annotation):
    """
    A dataclass representing the properties of a PDF link annotation.

    This class extends the `Annotation` base class to specifically handle
    link annotations, including the target URI or an internal page.

    Attributes:
        uri (str): The URI that the link annotation points to. Defaults to None.
        page (int): The 1-based page number that the link annotation points to. Defaults to None.
    """

    _annotation_type: str = "/Link"

    uri: Optional[str] = None
    page: Optional[int] = None

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the link annotation.

        This method extends the base properties with either a URI action
        or a destination for an internal page link.

        Returns:
            dict: A dictionary of PDF properties specific to the link annotation.
        """
        result = super().get_specific_properties()
        if self.uri is not None:
            result[NameObject(A)] = DictionaryObject(
                {
                    NameObject(S): NameObject("/URI"),
                    NameObject("/URI"): TextStringObject(self.uri),
                }
            )
        elif self.page is not None:
            result[NameObject("/Dest")] = ArrayObject(
                [NumberObject(self.page - 1), NameObject("/Fit")]
            )

        return result
