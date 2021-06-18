# -*- coding: utf-8 -*-
"""Contains patterns used for identifying properties of elements."""

from ..middleware.element import ElementType
from .constants import Template

ELEMENT_TYPE_PATTERNS = [
    (
        ({Template().element_type_key: Template().text_field_identifier},),
        ElementType.text,
    ),
    (
        ({Template().element_type_key: Template().selectable_identifier},),
        ElementType.checkbox,
    ),
    (
        (
            {
                Template().parent_key: {
                    Template().element_type_key: Template().text_field_identifier
                }
            },
        ),
        ElementType.text,
    ),
    (
        (
            {
                Template().parent_key: {
                    Template().element_type_key: Template().selectable_identifier
                }
            },
            {
                Template().parent_key: {
                    Template().subtype_key: Template().widget_subtype_key
                }
            },
        ),
        ElementType.checkbox,
    ),
    (
        (
            {
                Template().parent_key: {
                    Template().element_type_key: Template().selectable_identifier
                }
            },
        ),
        ElementType.radio,
    ),
]

ELEMENT_KEY_PATTERNS = [
    {Template().annotation_field_key: True},
    {Template().parent_key: {Template().annotation_field_key: True}},
]
