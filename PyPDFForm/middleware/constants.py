# -*- coding: utf-8 -*-


class PDF(object):
    @property
    def annotation_key(self):
        return "/Annots"

    @property
    def annotation_field_key(self):
        return "/T"

    @property
    def annotation_rectangle_key(self):
        return "/Rect"

    @property
    def subtype_key(self):
        return "/Subtype"

    @property
    def widget_subtype_key(self):
        return "/Widget"

    @property
    def element_type_key(self):
        return "/FT"
