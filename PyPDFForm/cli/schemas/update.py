# -*- coding: utf-8 -*-
# pylint: disable=R0801
"""
JSON schemas for the PyPDFForm update CLI commands.
"""

RENAME_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "minProperties": 1,
        "maxProperties": 1,
        "additionalProperties": {
            "type": "object",
            "properties": {
                "new_key": {"type": "string"},
                "index": {"type": "integer", "minimum": 0},
            },
            "required": ["new_key"],
            "additionalProperties": False,
        },
    },
}

FIELD_SCHEMA = {
    "type": "object",
    "patternProperties": {
        ".+": {
            "type": "object",
            "properties": {
                "x": {
                    "anyOf": [
                        {"type": "number"},
                        {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 1,
                        },
                    ]
                },
                "y": {
                    "anyOf": [
                        {"type": "number"},
                        {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 1,
                        },
                    ]
                },
                "width": {
                    "anyOf": [
                        {"type": "number"},
                        {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 1,
                        },
                    ]
                },
                "height": {
                    "anyOf": [
                        {"type": "number"},
                        {
                            "type": "array",
                            "items": {"type": "number"},
                            "minItems": 1,
                        },
                    ]
                },
                "readonly": {"type": "boolean"},
                "required": {"type": "boolean"},
                "hidden": {"type": "boolean"},
                "tooltip": {"type": "string"},
                "on_hovered_over_javascript": {"type": "string"},
                "on_hovered_off_javascript": {"type": "string"},
                "on_mouse_pressed_javascript": {"type": "string"},
                "on_mouse_released_javascript": {"type": "string"},
                "on_focused_javascript": {"type": "string"},
                "on_blurred_javascript": {"type": "string"},
                "font": {"type": "string"},
                "font_size": {"type": "number"},
                "font_color": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 3,
                    "maxItems": 3,
                },
                "comb": {"type": "boolean"},
                "alignment": {"type": "integer", "minimum": 0, "maximum": 2},
                "multiline": {"type": "boolean"},
                "max_length": {"type": "integer", "minimum": 0},
                "choices": {
                    "type": "array",
                    "items": {
                        "anyOf": [
                            {"type": "string"},
                            {
                                "type": "array",
                                "items": {"type": "string"},
                                "minItems": 2,
                                "maxItems": 2,
                            },
                        ]
                    },
                    "minItems": 1,
                },
                "size": {"type": "number"},
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}
