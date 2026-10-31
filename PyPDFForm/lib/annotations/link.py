# -*- coding: utf-8 -*-
"""
This module defines the class for link annotations in PyPDFForm.

It provides a structure for representing and interacting with PDF link
annotations, which allow users to click and navigate to a URI or an internal page.

Classes:
    - `LinkAnnotation`: A dataclass representing the properties of a PDF link annotation.
"""

from dataclasses import dataclass
from typing import Optional, Sequence

from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    IndirectObject,
    NameObject,
    TextStringObject,
)

from ..constants import A, Link, S
from .base import Annotation


@dataclass
class LinkAnnotation(Annotation):
    """
    A dataclass representing the properties of a PDF link annotation.

    This class extends the `Annotation` base class to specifically handle
    link annotations, including the target URI or an internal page.

    Attributes:
        uri (str): The URI that the link annotation points to. Takes precedence
            over `page` when both are set. Defaults to None.
        page (int): The 1-based page number in the same PDF that the link
            annotation points to. Defaults to None.
    """

    _annotation_type: str = Link

    uri: Optional[str] = None
    page: Optional[int] = None

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the link annotation.

        This method extends the base properties with a URI action. A link to
        an internal page needs the pages of the target PDF, so its destination
        is built separately by `get_destination`.

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

        return result

    def get_destination(
        self, page_references: Sequence[IndirectObject]
    ) -> Optional[ArrayObject]:
        """
        Gets the destination of a link to an internal page.

        A destination in the same PDF must refer to the target page object
        rather than a page index, which is reserved for destinations in other
        PDFs. The 1-based `page` is resolved against the page references of the
        PDF that will contain the link.

        Args:
            page_references (Sequence[IndirectObject]): References to the pages
                of the PDF that will contain the link, in page order.

        Returns:
            Optional[ArrayObject]: The destination that fits the target page in
                the window, or None if the link has a URI or no page.

        Raises:
            ValueError: If `page` is outside the pages of the PDF.
        """
        if self.uri is not None or self.page is None:
            return None

        if not 1 <= self.page <= len(page_references):
            msg = f"Link page {self.page} must satisfy 1 <= page <= {len(page_references)}."
            raise ValueError(msg)

        return ArrayObject([page_references[self.page - 1], NameObject("/Fit")])
