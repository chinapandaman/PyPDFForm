# -*- coding: utf-8 -*-
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
                "font_size": {"type": "number", "minimum": 0},
                "font_color": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 0, "maximum": 1},
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
                "size": {"type": "number", "minimum": 0},
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}
