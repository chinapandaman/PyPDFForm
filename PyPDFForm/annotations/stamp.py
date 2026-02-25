# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from pypdf.generic import NameObject

from .base import Annotation


@dataclass
class RubberStampAnnotation(Annotation):
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
        result = super().get_specific_properties()
        if self.name is not None:
            result[NameObject("/Name")] = NameObject(self.name)

        return result
