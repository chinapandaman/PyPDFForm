# -*- coding: utf-8 -*-
# pylint: disable=R0801
"""
JSON schemas for the PyPDFForm create CLI commands.
"""

FIELD_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "required": {"type": "boolean"},
                    "tooltip": {"type": "string"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "font": {"type": "string"},
                    "font_size": {"type": "number"},
                    "font_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_width": {"type": "number"},
                    "max_length": {"type": "integer", "minimum": 1},
                    "comb": {"type": "boolean"},
                    "alignment": {"type": "integer", "minimum": 0, "maximum": 2},
                    "multiline": {"type": "boolean"},
                },
                "required": ["name", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "check": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "required": {"type": "boolean"},
                    "tooltip": {"type": "string"},
                    "size": {"type": "number"},
                    "button_style": {"type": "string"},
                    "tick_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_width": {"type": "number"},
                },
                "required": ["name", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "radio": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 1,
                    },
                    "y": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 1,
                    },
                    "required": {"type": "boolean"},
                    "tooltip": {"type": "string"},
                    "size": {"type": "number"},
                    "button_style": {"type": "string"},
                    "tick_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_width": {"type": "number"},
                    "shape": {"type": "string"},
                },
                "required": ["name", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "dropdown": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "required": {"type": "boolean"},
                    "tooltip": {"type": "string"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "font": {"type": "string"},
                    "font_size": {"type": "number"},
                    "font_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                    "bg_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "border_width": {"type": "number"},
                    "options": {
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
                },
                "required": ["name", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "image": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "required": {"type": "boolean"},
                    "tooltip": {"type": "string"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                },
                "required": ["name", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "signature": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "required": {"type": "boolean"},
                    "tooltip": {"type": "string"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                },
                "required": ["name", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

RAW_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "font": {"type": "string"},
                    "font_size": {"type": "number"},
                    "font_color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 3,
                    },
                },
                "required": ["text", "page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "image": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "image": {"type": "string"},
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "rotation": {"type": "number"},
                },
                "required": ["image", "page_number", "x", "y", "width", "height"],
                "additionalProperties": False,
            },
        },
        "line": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "src_x": {"type": "number"},
                    "src_y": {"type": "number"},
                    "dest_x": {"type": "number"},
                    "dest_y": {"type": "number"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                },
                "required": ["page_number", "src_x", "src_y", "dest_x", "dest_y"],
                "additionalProperties": False,
            },
        },
        "rectangle": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "fill_color": {
                        "anyOf": [
                            {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 4,
                            },
                            {"type": "null"},
                        ]
                    },
                },
                "required": ["page_number", "x", "y", "width", "height"],
                "additionalProperties": False,
            },
        },
        "circle": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "center_x": {"type": "number"},
                    "center_y": {"type": "number"},
                    "radius": {"type": "number"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "fill_color": {
                        "anyOf": [
                            {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 4,
                            },
                            {"type": "null"},
                        ]
                    },
                },
                "required": ["page_number", "center_x", "center_y", "radius"],
                "additionalProperties": False,
            },
        },
        "ellipse": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x1": {"type": "number"},
                    "y1": {"type": "number"},
                    "x2": {"type": "number"},
                    "y2": {"type": "number"},
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 3,
                        "maxItems": 4,
                    },
                    "fill_color": {
                        "anyOf": [
                            {
                                "type": "array",
                                "items": {"type": "number"},
                                "minItems": 3,
                                "maxItems": 4,
                            },
                            {"type": "null"},
                        ]
                    },
                },
                "required": ["page_number", "x1", "y1", "x2", "y2"],
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

ANNOTATION_SCHEMA = {
    "type": "object",
    "properties": {
        "text": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                    "title": {"type": "string"},
                    "icon": {"type": "string"},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "link": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                    "uri": {"type": "string"},
                    "page": {"type": "integer", "minimum": 1},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "highlight": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "underline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "squiggly": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "strikeout": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
        "stamp": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "minimum": 1},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "contents": {"type": "string"},
                    "name": {"type": "string"},
                },
                "required": ["page_number", "x", "y"],
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}
