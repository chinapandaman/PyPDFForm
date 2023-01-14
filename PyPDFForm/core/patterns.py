# -*- coding: utf-8 -*-
"""Contains patterns used for identifying properties of elements."""

from ..middleware.element import ElementType
from . import constants

ELEMENT_TYPE_PATTERNS = [
    (
        ({constants.ELEMENT_TYPE_KEY: constants.TEXT_FIELD_IDENTIFIER},),
        ElementType.text,
    ),
    (
        ({constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER},),
        ElementType.checkbox,
    ),
    (
        (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.TEXT_FIELD_IDENTIFIER
                }
            },
        ),
        ElementType.text,
    ),
    (
        (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER
                }
            },
            {
                constants.PARENT_KEY: {
                    constants.SUBTYPE_KEY: constants.WIDGET_SUBTYPE_KEY
                }
            },
        ),
        ElementType.checkbox,
    ),
    (
        (
            {
                constants.PARENT_KEY: {
                    constants.ELEMENT_TYPE_KEY: constants.SELECTABLE_IDENTIFIER
                }
            },
        ),
        ElementType.radio,
    ),
]

ELEMENT_KEY_PATTERNS = [
    {constants.ANNOTATION_FIELD_KEY: True},
    {constants.PARENT_KEY: {constants.ANNOTATION_FIELD_KEY: True}},
]
