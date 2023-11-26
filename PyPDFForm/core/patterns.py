# -*- coding: utf-8 -*-
"""Contains patterns used for identifying properties of elements."""

from ..middleware.checkbox import Checkbox
from ..middleware.dropdown import Dropdown
from ..middleware.radio import Radio
from ..middleware.text import Text
from .constants import ELEMENT_TYPE_KEY, TEXT_FIELD_IDENTIFIER, \
    SELECTABLE_IDENTIFIER, CHOICE_FIELD_IDENTIFIER, \
    PARENT_KEY, SUBTYPE_KEY, WIDGET_SUBTYPE_KEY, \
    ANNOTATION_FIELD_KEY, CHOICES_IDENTIFIER, \
    TEXT_FIELD_ALIGNMENT_IDENTIFIER, FIELD_FLAG_KEY, \
    TEXT_FIELD_APPEARANCE_IDENTIFIER

ELEMENT_TYPE_PATTERNS = [
    (
        ({ELEMENT_TYPE_KEY: TEXT_FIELD_IDENTIFIER},),
        Text,
    ),
    (
        ({ELEMENT_TYPE_KEY: SELECTABLE_IDENTIFIER},),
        Checkbox,
    ),
    (
        ({ELEMENT_TYPE_KEY: CHOICE_FIELD_IDENTIFIER},),
        Dropdown,
    ),
    (
        (
            {
                PARENT_KEY: {
                    ELEMENT_TYPE_KEY: CHOICE_FIELD_IDENTIFIER
                }
            },
        ),
        Dropdown,
    ),
    (
        (
            {
                PARENT_KEY: {
                    ELEMENT_TYPE_KEY: TEXT_FIELD_IDENTIFIER
                }
            },
        ),
        Text,
    ),
    (
        (
            {
                PARENT_KEY: {
                    ELEMENT_TYPE_KEY: SELECTABLE_IDENTIFIER
                }
            },
            {
                PARENT_KEY: {
                    SUBTYPE_KEY: WIDGET_SUBTYPE_KEY
                }
            },
        ),
        Checkbox,
    ),
    (
        (
            {
                PARENT_KEY: {
                    ELEMENT_TYPE_KEY: SELECTABLE_IDENTIFIER
                }
            },
        ),
        Radio,
    ),
]

ELEMENT_KEY_PATTERNS = [
    {ANNOTATION_FIELD_KEY: True},
    {PARENT_KEY: {ANNOTATION_FIELD_KEY: True}},
]

DROPDOWN_CHOICE_PATTERNS = [
    {CHOICES_IDENTIFIER: True},
    {PARENT_KEY: {CHOICES_IDENTIFIER: True}},
]

ELEMENT_ALIGNMENT_PATTERNS = [
    {TEXT_FIELD_ALIGNMENT_IDENTIFIER: True},
    {PARENT_KEY: {TEXT_FIELD_ALIGNMENT_IDENTIFIER: True}},
]

TEXT_FIELD_FLAG_PATTERNS = [
    {FIELD_FLAG_KEY: True},
    {PARENT_KEY: {FIELD_FLAG_KEY: True}},
]

TEXT_FIELD_APPEARANCE_PATTERNS = [
    {TEXT_FIELD_APPEARANCE_IDENTIFIER: True},
    {PARENT_KEY: {TEXT_FIELD_APPEARANCE_IDENTIFIER: True}},
]
