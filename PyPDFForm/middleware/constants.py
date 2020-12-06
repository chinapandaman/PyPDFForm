# -*- coding: utf-8 -*-


class Template(object):
    @property
    def annotation_key(self) -> str:
        """Used for parsing PDF form via pdfrw."""

        return "/Annots"

    @property
    def annotation_field_key(self) -> str:
        """Used for parsing PDF form via pdfrw."""

        return "/T"

    @property
    def annotation_rectangle_key(self) -> str:
        """Used for parsing PDF form via pdfrw."""

        return "/Rect"

    @property
    def subtype_key(self) -> str:
        """Used for parsing PDF form via pdfrw."""

        return "/Subtype"

    @property
    def widget_subtype_key(self) -> str:
        """Used for parsing PDF form via pdfrw."""

        return "/Widget"

    @property
    def element_type_key(self) -> str:
        """Used for parsing PDF form via pdfrw."""

        return "/FT"
