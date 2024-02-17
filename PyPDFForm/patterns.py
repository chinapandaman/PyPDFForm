# -*- coding: utf-8 -*-
"""Contains patterns used for identifying properties of widgets."""

from .constants import (ANNOTATION_FIELD_KEY, BUTTON_IDENTIFIER,
                        BUTTON_STYLE_IDENTIFIER, CHOICE_FIELD_IDENTIFIER,
                        CHOICES_IDENTIFIER, FIELD_FLAG_KEY, PARENT_KEY,
                        SELECTABLE_IDENTIFIER, SIGNATURE_FIELD_IDENTIFIER,
                        SUBTYPE_KEY, TEXT_FIELD_ALIGNMENT_IDENTIFIER,
                        TEXT_FIELD_APPEARANCE_IDENTIFIER,
                        TEXT_FIELD_IDENTIFIER, WIDGET_SUBTYPE_KEY,
                        WIDGET_TYPE_KEY)
from .middleware.checkbox import Checkbox
from .middleware.dropdown import Dropdown
from .middleware.radio import Radio
from .middleware.signature import Signature
from .middleware.text import Text

WIDGET_TYPE_PATTERNS = [
    (
        ({WIDGET_TYPE_KEY: SIGNATURE_FIELD_IDENTIFIER},),
        Signature,
    ),
    (
        ({WIDGET_TYPE_KEY: TEXT_FIELD_IDENTIFIER},),
        Text,
    ),
    (
        ({WIDGET_TYPE_KEY: SELECTABLE_IDENTIFIER},),
        Checkbox,
    ),
    (
        ({WIDGET_TYPE_KEY: CHOICE_FIELD_IDENTIFIER},),
        Dropdown,
    ),
    (
        ({PARENT_KEY: {WIDGET_TYPE_KEY: CHOICE_FIELD_IDENTIFIER}},),
        Dropdown,
    ),
    (
        ({PARENT_KEY: {WIDGET_TYPE_KEY: TEXT_FIELD_IDENTIFIER}},),
        Text,
    ),
    (
        (
            {PARENT_KEY: {WIDGET_TYPE_KEY: SELECTABLE_IDENTIFIER}},
            {PARENT_KEY: {SUBTYPE_KEY: WIDGET_SUBTYPE_KEY}},
        ),
        Checkbox,
    ),
    (
        ({PARENT_KEY: {WIDGET_TYPE_KEY: SELECTABLE_IDENTIFIER}},),
        Radio,
    ),
]

WIDGET_KEY_PATTERNS = [
    {ANNOTATION_FIELD_KEY: True},
    {PARENT_KEY: {ANNOTATION_FIELD_KEY: True}},
]

DROPDOWN_CHOICE_PATTERNS = [
    {CHOICES_IDENTIFIER: True},
    {PARENT_KEY: {CHOICES_IDENTIFIER: True}},
]

WIDGET_ALIGNMENT_PATTERNS = [
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

BUTTON_STYLE_PATTERNS = [
    {BUTTON_IDENTIFIER: {BUTTON_STYLE_IDENTIFIER: True}},
]
