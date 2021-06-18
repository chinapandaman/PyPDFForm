# -*- coding: utf-8 -*-
"""Contains patterns used for identifying properties of elements."""

from .constants import Template
from ..middleware.element import ElementType


ELEMENT_TYPE_PATTERNS = [
    (({Template().element_type_key: "/Tx"},), ElementType.text),
    (
        ({Template().element_type_key: "/Btn"},),
        ElementType.checkbox,
    ),
    (
        (
            {
                Template().parent_key: {
                    Template().element_type_key: "/Tx"
                }
            },
        ),
        ElementType.text,
    ),
    (
        (
            {
                Template().parent_key: {
                    Template().element_type_key: "/Btn"
                }
            },
            {
                Template().parent_key: {
                    Template()
                    .subtype_key: Template()
                    .widget_subtype_key
                }
            },
        ),
        ElementType.checkbox,
    ),
    (
        (
            {
                Template().parent_key: {
                    Template().element_type_key: "/Btn"
                }
            },
        ),
        ElementType.radio,
    ),
]

ELEMENT_KEY_PATTERNS = [
    {Template().annotation_field_key: True},
    {
        Template().parent_key: {
            Template().annotation_field_key: True
        }
    },
]
