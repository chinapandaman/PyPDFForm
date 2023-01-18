# -*- coding: utf-8 -*-
"""Contains helpers for filling a PDF form."""

from copy import deepcopy
from typing import Dict, Union

import pdfrw
from pdfrw.objects.pdfname import BasePdfName

from ..middleware.element import Element as ElementMiddleware
from ..middleware.element import ElementType
from . import constants, template, utils
from . import watermark as watermark_core


def fill(
    template_stream: bytes,
    elements: Dict[str, ElementMiddleware],
    sejda: bool = False,
) -> bytes:
    """Fills a PDF using watermarks."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)

    texts_to_draw = {}
    text_watermarks = []

    radio_button_tracker = {}

    for page, _elements in template.get_elements_by_page(template_pdf, sejda).items():
        texts_to_draw[page] = []
        text_watermarks.append(b"")
        for _element in _elements:
            key = template.get_element_key(_element, sejda)

            update_dict = {
                constants.FIELD_FLAG_KEY.replace("/", ""): pdfrw.PdfObject(1)
            }
            if elements[key].type == ElementType.checkbox:
                if sejda and elements[key].value is True:
                    texts_to_draw[page].append(
                        [
                            utils.checkbox_radio_to_draw(elements[key]),
                            template.get_draw_checkbox_radio_coordinates(_element)[0],
                            template.get_draw_checkbox_radio_coordinates(_element)[1],
                        ]
                    )
                else:
                    update_dict[
                        constants.CHECKBOX_FIELD_VALUE_KEY.replace("/", "")
                    ] = utils.bool_to_checkbox(elements[key].value)
            elif elements[key].type == ElementType.radio:
                if key not in radio_button_tracker:
                    radio_button_tracker[key] = 0
                radio_button_tracker[key] += 1

                if elements[key].value == radio_button_tracker[key] - 1:
                    if sejda:
                        texts_to_draw[page].append(
                            [
                                utils.checkbox_radio_to_draw(elements[key]),
                                template.get_draw_checkbox_radio_coordinates(_element)[
                                    0
                                ],
                                template.get_draw_checkbox_radio_coordinates(_element)[
                                    1
                                ],
                            ]
                        )
                    else:
                        _element.update(
                            pdfrw.PdfDict(
                                **{
                                    constants.CHECKBOX_FIELD_VALUE_KEY.replace(
                                        "/", ""
                                    ): BasePdfName(
                                        "/" + str(elements[key].value), False
                                    ),
                                }
                            )
                        )

                _element[constants.PARENT_KEY].update(
                    pdfrw.PdfDict(
                        **{
                            constants.FIELD_FLAG_KEY.replace("/", ""): pdfrw.PdfObject(
                                1
                            )
                        }
                    )
                )
                continue
            else:
                texts_to_draw[page].append(
                    [
                        elements[key],
                        template.get_draw_text_coordinates(_element)[0],
                        template.get_draw_text_coordinates(_element)[1],
                    ]
                )
            if sejda:
                _element[constants.PARENT_KEY].update(pdfrw.PdfDict(**update_dict))
            else:
                _element.update(pdfrw.PdfDict(**update_dict))

    for page, texts in texts_to_draw.items():
        _watermarks = watermark_core.create_watermarks_and_draw(
            template_stream, page, "text", texts
        )
        for i, watermark in enumerate(_watermarks):
            if watermark:
                text_watermarks[i] = watermark

    return watermark_core.merge_watermarks_with_pdf(
        utils.generate_stream(template_pdf), text_watermarks
    )


def simple_fill(
    template_stream: bytes,
    data: Dict[str, Union[str, bool, int]],
    editable: bool,
) -> bytes:
    """Fills a PDF form in simple mode."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)
    data = utils.bool_to_checkboxes(data)

    radio_button_tracker = {}

    for element in template.iterate_elements(template_pdf):
        key = template.get_element_key(element)

        if key in data.keys():
            update_dict = {}
            if data[key] in [
                pdfrw.PdfName.Yes,
                pdfrw.PdfName.Off,
            ]:
                update_dict = {
                    constants.CHECKBOX_FIELD_VALUE_KEY.replace("/", ""): data[key]
                }
            elif isinstance(data[key], int):
                if key not in radio_button_tracker:
                    radio_button_tracker[key] = 0
                radio_button_tracker[key] += 1

                if data[key] == radio_button_tracker[key] - 1:
                    element.update(
                        pdfrw.PdfDict(
                            **{
                                constants.CHECKBOX_FIELD_VALUE_KEY.replace(
                                    "/", ""
                                ): BasePdfName("/" + str(data[key]), False),
                            }
                        )
                    )

                    if not editable:
                        element[constants.PARENT_KEY].update(
                            pdfrw.PdfDict(
                                **{
                                    constants.FIELD_FLAG_KEY.replace(
                                        "/", ""
                                    ): pdfrw.PdfObject(1)
                                }
                            )
                        )
                    continue
            else:
                update_dict = {
                    constants.TEXT_FIELD_VALUE_KEY.replace("/", ""): data[key]
                }

            if not editable:
                update_dict[
                    constants.FIELD_FLAG_KEY.replace("/", "")
                ] = pdfrw.PdfObject(1)

            element.update(pdfrw.PdfDict(**update_dict))

    return utils.generate_stream(template_pdf)


def fill_v2(
    template_stream: bytes,
    elements: Dict[str, ElementMiddleware],
) -> bytes:
    """Fills a PDF using watermarks."""

    template_pdf = pdfrw.PdfReader(fdata=template_stream)

    texts_to_draw = {}
    text_watermarks = []

    radio_button_tracker = {}

    for page, _elements in template.get_elements_by_page_v2(template_pdf).items():
        texts_to_draw[page] = []
        text_watermarks.append(b"")
        for _element in _elements:
            key = template.get_element_key_v2(_element)

            if elements[key].type == ElementType.checkbox:
                if elements[key].value:
                    font_size = utils.checkbox_radio_font_size(_element)
                    _to_draw = utils.checkbox_radio_to_draw(elements[key], font_size)
                    x, y = template.get_draw_checkbox_radio_coordinates_v2(
                        _element, _to_draw
                    )
                    texts_to_draw[page].append(
                        [
                            _to_draw,
                            x,
                            y,
                        ]
                    )
            elif elements[key].type == ElementType.radio:
                if key not in radio_button_tracker:
                    radio_button_tracker[key] = 0
                radio_button_tracker[key] += 1

                if elements[key].value == radio_button_tracker[key] - 1:
                    font_size = utils.checkbox_radio_font_size(_element)
                    _to_draw = utils.checkbox_radio_to_draw(elements[key], font_size)
                    x, y = template.get_draw_checkbox_radio_coordinates_v2(
                        _element, _to_draw
                    )
                    texts_to_draw[page].append(
                        [
                            _to_draw,
                            x,
                            y,
                        ]
                    )
            elif elements[key].type == ElementType.dropdown:
                ele = deepcopy(elements[key])
                ele.value = (
                    ele.choices[ele.value] if ele.value < len(ele.choices) else ""
                )
                x, y = template.get_draw_text_coordinates_v2(_element, ele)
                texts_to_draw[page].append(
                    [
                        ele,
                        x,
                        y,
                    ]
                )
            else:
                x, y = template.get_draw_text_coordinates_v2(_element, elements[key])
                texts_to_draw[page].append(
                    [
                        elements[key],
                        x,
                        y,
                    ]
                )

    for page, texts in texts_to_draw.items():
        _watermarks = watermark_core.create_watermarks_and_draw(
            template_stream, page, "text", texts
        )
        for i, watermark in enumerate(_watermarks):
            if watermark:
                text_watermarks[i] = watermark

    return watermark_core.merge_watermarks_with_pdf(
        utils.generate_stream(template_pdf), text_watermarks
    )
