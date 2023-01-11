# -*- coding: utf-8 -*-
"""Contains constants used for core layer."""

ANNOTATION_KEY = "/Annots"
ANNOTATION_FIELD_KEY = "/T"
ANNOTATION_RECTANGLE_KEY = "/Rect"
SUBTYPE_KEY = "/Subtype"
WIDGET_SUBTYPE_KEY = "/Widget"
ELEMENT_TYPE_KEY = "/FT"
TEXT_FIELD_VALUE_KEY = "/V"
CHECKBOX_FIELD_VALUE_KEY = "/AS"
PARENT_KEY = "/Parent"
FIELD_FLAG_KEY = "/Ff"
TEXT_FIELD_IDENTIFIER = "/Tx"
SELECTABLE_IDENTIFIER = "/Btn"
TEXT_FIELD_MAX_LENGTH_KEY = "/MaxLen"
TEXT_FIELD_ALIGNMENT_IDENTIFIER = "/Q"

SEPARATOR = "_e65c5a97ecc14cf79e4e86f5365be93b_"


class Merge:
    """Contains constants for merging PDFs."""

    @property
    def separator(self) -> str:
        """Used for separating uuid from annotated name."""

        return "_e65c5a97ecc14cf79e4e86f5365be93b_"
