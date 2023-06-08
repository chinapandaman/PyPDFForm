# -*- coding: utf-8 -*-
"""Contains helpers for calculating font size."""

from typing import Dict

import pdfrw

from ..middleware.text import Text
from ..middleware.constants import ELEMENT_TYPES
from . import template


def update_text_field_font_sizes(
        template_stream: bytes,
        elements: Dict[str, ELEMENT_TYPES],
        ) -> None:
    """Updates text fields' font sizes."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)

    for _, _elements in template.get_elements_by_page(template_pdf).items():
        for _element in _elements:
            key = template.get_element_key(_element)

            if isinstance(elements[key], Text) and elements[key].font_size is None:
                elements[key].font_size = template.get_text_field_font_size(_element) or 12
