# -*- coding: utf-8 -*-
"""
This module defines the `RubberStampAnnotation` class, which is used to represent
a rubber stamp annotation in a PDF document.

The `RubberStampAnnotation` class encapsulates the properties of a rubber stamp
annotation, such as its location, dimensions, content, and the stamp name.
"""

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import NameObject

from .base import Annotation


@dataclass
class RubberStampAnnotation(Annotation):
    """
    Represents a rubber stamp annotation in a PDF document.

    This dataclass extends the base `Annotation` class and defines the specific
    attributes and metadata associated with a rubber stamp annotation.

    Attributes:
        _annotation_type (str): The PDF internal type of the annotation, which is "/Stamp".
        approved (str): The identifier for an "Approved" stamp.
        experimental (str): The identifier for an "Experimental" stamp.
        not_approved (str): The identifier for a "NotApproved" stamp.
        as_is (str): The identifier for an "AsIs" stamp.
        expired (str): The identifier for an "Expired" stamp.
        not_for_public_release (str): The identifier for a "NotForPublicRelease" stamp.
        confidential (str): The identifier for a "Confidential" stamp.
        final (str): The identifier for a "Final" stamp.
        sold (str): The identifier for a "Sold" stamp.
        departmental (str): The identifier for a "Departmental" stamp.
        for_comment (str): The identifier for a "ForComment" stamp.
        top_secret (str): The identifier for a "TopSecret" stamp.
        draft (str): The identifier for a "Draft" stamp.
        for_public_release (str): The identifier for a "ForPublicRelease" stamp.
        name (Optional[str]): The name of the stamp to be used.
    """

    _annotation_type: str = "/Stamp"

    approved = "/Approved"
    experimental = "/Experimental"
    not_approved = "/NotApproved"
    as_is = "/AsIs"
    expired = "/Expired"
    not_for_public_release = "/NotForPublicRelease"
    confidential = "/Confidential"
    final = "/Final"
    sold = "/Sold"
    departmental = "/Departmental"
    for_comment = "/ForComment"
    top_secret = "/TopSecret"
    draft = "/Draft"
    for_public_release = "/ForPublicRelease"

    name: Optional[str] = None

    def get_specific_properties(self) -> dict:
        """
        Gets properties specific to the rubber stamp annotation.

        This method extends the base properties with the stamp name if it is provided.

        Returns:
            dict: A dictionary of PDF properties specific to the rubber stamp annotation.
        """
        result = super().get_specific_properties()
        if self.name is not None:
            result[NameObject("/Name")] = NameObject(self.name)

        return result
