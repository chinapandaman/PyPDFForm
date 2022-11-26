# -*- coding: utf-8 -*-
"""Contains constants used for core layer."""


class Template:
    """Contains constants for pdfrw parsed PDF form."""

    @property
    def annotation_key(self) -> str:
        """Used for extracting elements from pdfrw parsed PDF form."""

        return "/Annots"

    @property
    def annotation_field_key(self) -> str:
        """Used for extracting elements from pdfrw parsed PDF form."""

        return "/T"

    @property
    def annotation_rectangle_key(self) -> str:
        """Used for extracting elements from pdfrw parsed PDF form."""

        return "/Rect"

    @property
    def subtype_key(self) -> str:
        """Used for extracting elements from pdfrw parsed PDF form."""

        return "/Subtype"

    @property
    def widget_subtype_key(self) -> str:
        """Used for extracting elements from pdfrw parsed PDF form."""

        return "/Widget"

    @property
    def element_type_key(self) -> str:
        """Used for extracting elements from pdfrw parsed PDF form."""

        return "/FT"

    @property
    def text_field_value_key(self) -> str:
        """Used for extracting text element values for pdfrw parsed PDF form."""

        return "/V"

    @property
    def checkbox_field_value_key(self) -> str:
        """Used for extracting checkbox element values for pdfrw parsed PDF form."""

        return "/AS"

    @property
    def parent_key(self) -> str:
        """Used for extracting parent elements for pdfrw parsed PDF form."""

        return "/Parent"

    @property
    def field_flag_key(self) -> str:
        """Field flags specific to text fields."""

        return "/Ff"

    @property
    def text_field_identifier(self) -> str:
        """Used for identifying if an element is a text field."""

        return "/Tx"

    @property
    def selectable_identifier(self) -> str:
        """Used for identifying if an element is a checkbox or radio button."""

        return "/Btn"

    @property
    def text_field_max_length_key(self) -> str:
        """Used for identifying a text field's max number of characters allowed."""

        return "/MaxLen"

    @property
    def text_field_alignment_identifier(self) -> str:
        """Used for identifying the text alignment of a text field."""

        return "/Q"


class Merge:
    """Contains constants for merging PDFs."""

    @property
    def separator(self) -> str:
        """Used for separating uuid from annotated name."""

        return "_e65c5a97ecc14cf79e4e86f5365be93b_"
