# -*- coding: utf-8 -*-
"""Contains helpers for template."""

import uuid
from typing import Dict, List, Tuple, Union

import pdfrw

from ..middleware.element import ElementType
from .constants import Merge as MergeConstants
from .constants import Template as TemplateCoreConstants
from .utils import Utils


class Template:
    """Contains methods for interacting with a pdfrw parsed PDF form."""

    @staticmethod
    def iterate_elements(
        pdf: Union[bytes, "pdfrw.PdfReader"], sejda: bool = False
    ) -> List["pdfrw.PdfDict"]:
        """Iterates through a PDF and returns all elements found."""

        if isinstance(pdf, bytes):
            pdf = pdfrw.PdfReader(fdata=pdf)

        result = []

        for i in range(len(pdf.pages)):
            elements = pdf.pages[i][TemplateCoreConstants().annotation_key]
            if elements:
                for element in elements:
                    if not sejda:
                        if (
                            element[TemplateCoreConstants().subtype_key]
                            == TemplateCoreConstants().widget_subtype_key
                            and element[TemplateCoreConstants().annotation_field_key]
                        ):
                            result.append(element)
                        elif (
                            element[TemplateCoreConstants().checkbox_field_value_key]
                            and element[TemplateCoreConstants().parent_key]
                        ):
                            result.append(element)
                    else:
                        if (
                            element[TemplateCoreConstants().parent_key]
                            and element[TemplateCoreConstants().parent_key][
                                TemplateCoreConstants().element_type_key
                            ]
                        ):
                            result.append(element)

        return result

    @staticmethod
    def get_elements_by_page(
        pdf: Union[bytes, "pdfrw.PdfReader"], sejda: bool = False
    ) -> Dict[int, List["pdfrw.PdfDict"]]:
        """Iterates through a PDF and returns all elements found grouped by page."""

        if isinstance(pdf, bytes):
            pdf = pdfrw.PdfReader(fdata=pdf)

        result = {}

        for i in range(len(pdf.pages)):
            elements = pdf.pages[i][TemplateCoreConstants().annotation_key]
            if elements:
                result[i + 1] = []
                for element in elements:
                    if not sejda:
                        if (
                            element[TemplateCoreConstants().subtype_key]
                            == TemplateCoreConstants().widget_subtype_key
                            and element[TemplateCoreConstants().annotation_field_key]
                        ):
                            result[i + 1].append(element)
                        elif (
                            element[TemplateCoreConstants().checkbox_field_value_key]
                            and element[TemplateCoreConstants().parent_key]
                        ):
                            result[i + 1].append(element)
                    else:
                        if (
                            element[TemplateCoreConstants().parent_key]
                            and element[TemplateCoreConstants().parent_key][
                                TemplateCoreConstants().element_type_key
                            ]
                        ):
                            result[i + 1].append(element)

        return result

    @staticmethod
    def get_element_key(element: "pdfrw.PdfDict", sejda: bool = False) -> str:
        """Returns its annotated key given a PDF form element."""

        if sejda:
            return element[TemplateCoreConstants().parent_key][
                TemplateCoreConstants().annotation_field_key
            ][1:-1]

        if not element[TemplateCoreConstants().annotation_field_key]:
            return element[TemplateCoreConstants().parent_key][
                TemplateCoreConstants().annotation_field_key
            ][1:-1]

        return element[TemplateCoreConstants().annotation_field_key][1:-1]

    @staticmethod
    def get_element_type(
        element: "pdfrw.PdfDict", sejda: bool = False
    ) -> Union["ElementType", None]:
        """Returns its annotated type given a PDF form element."""

        if sejda:
            if (
                element[TemplateCoreConstants().parent_key][
                    TemplateCoreConstants().element_type_key
                ]
                == "/Tx"
            ):
                return ElementType.text
            if (
                element[TemplateCoreConstants().parent_key][
                    TemplateCoreConstants().element_type_key
                ]
                == "/Btn"
            ):
                if (
                    element[TemplateCoreConstants().parent_key][
                        TemplateCoreConstants().subtype_key
                    ]
                    == TemplateCoreConstants().widget_subtype_key
                ):
                    return ElementType.checkbox
                return ElementType.radio

        element_type_mapping = {
            "/Btn": ElementType.checkbox,
            "/Tx": ElementType.text,
        }

        result = element_type_mapping.get(
            str(element[TemplateCoreConstants().element_type_key])
        )

        if not result and element[TemplateCoreConstants().parent_key]:
            return ElementType.radio

        return result

    @staticmethod
    def get_draw_checkbox_radio_coordinates(
            element: "pdfrw.PdfDict",
    ) -> Tuple[Union[float, int], Union[float, int]]:
        """Returns coordinates to draw checkbox/radio at given a PDF form text element."""

        return (
            (
                    float(element[TemplateCoreConstants().annotation_rectangle_key][0])
                    + float(element[TemplateCoreConstants().annotation_rectangle_key][2])
            )
            / 2 - 5,
            (
                    float(element[TemplateCoreConstants().annotation_rectangle_key][1])
                    + float(element[TemplateCoreConstants().annotation_rectangle_key][3])
            )
            / 2 - 4,
        )

    @staticmethod
    def get_draw_text_coordinates(
        element: "pdfrw.PdfDict",
    ) -> Tuple[Union[float, int], Union[float, int]]:
        """Returns coordinates to draw text at given a PDF form text element."""

        return (
            float(element[TemplateCoreConstants().annotation_rectangle_key][0]),
            (
                float(element[TemplateCoreConstants().annotation_rectangle_key][1])
                + float(element[TemplateCoreConstants().annotation_rectangle_key][3])
            )
            / 2
            - 2,
        )

    def assign_uuid(self, pdf: bytes, sejda: bool = False) -> bytes:
        """Appends a separator and uuid after each element's annotated name."""

        _uuid = uuid.uuid4().hex

        pdf_file = pdfrw.PdfReader(fdata=pdf)

        for element in self.iterate_elements(pdf_file):
            base_key = self.get_element_key(element)
            existed_uuid = ""
            if MergeConstants().separator in base_key:
                base_key, existed_uuid = base_key.split(MergeConstants().separator)

            update_dict = {
                TemplateCoreConstants().annotation_field_key.replace(
                    "/", ""
                ): "{}{}{}".format(
                    base_key, MergeConstants().separator, existed_uuid or _uuid
                )
            }
            if sejda:
                element[TemplateCoreConstants().parent_key].update(pdfrw.PdfDict(**update_dict))
            else:
                element.update(pdfrw.PdfDict(**update_dict))

        return Utils().generate_stream(pdf_file)
