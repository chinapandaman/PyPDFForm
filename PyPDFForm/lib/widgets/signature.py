# -*- coding: utf-8 -*-
# pylint: disable=R0801
"""
This module defines the `SignatureField` and `SignatureWidget` classes, which are
used to describe and construct signature form fields.

`SignatureField` stores the user-facing field definition. `SignatureWidget`
normalizes that definition's values, constructs a `/Sig` widget annotation,
and packages annotations in page-aligned PDFs so they can be copied into the
destination document.

Signature annotations and their appearance streams are constructed directly;
they do not depend on ReportLab's AcroForm API or an external template PDF.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Callable, List, Optional, Type

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)
from reportlab.pdfgen.canvas import Canvas

from ..constants import AP, DA, FT, Annot, Annots, F, N, Rect, S, Sig, Subtype, T
from ..constants import Type as PdfType
from .base import Field


class SignatureWidget:
    """
    Represents a signature widget in a PDF form.

    The widget stores placement, dimensions, and deferred hook values for a
    signature field. Unlike widgets backed by ReportLab's AcroForm API, it
    constructs its PDF annotation and normal appearance stream directly.

    Attributes:
        OPTIONAL_PARAMS (list): Width and height parameters with their defaults.
        ALLOWED_HOOK_PARAMS (list): Parameters applied after the annotation has
            been copied into the destination PDF.
    """

    OPTIONAL_PARAMS = [
        ("width", 160),
        ("height", 90),
    ]
    ALLOWED_HOOK_PARAMS = ["required", "tooltip"]

    def __init__(
        self,
        name: str,
        page_number: int,
        x: float,
        y: float,
        **kwargs,
    ) -> None:
        """
        Initializes a signature widget description.

        The widget records placement information, resolves width and height with
        defaults of 160 and 90 points, and captures `required` and `tooltip`
        values for later application.

        Args:
            name (str): The name of the signature widget.
            page_number (int): The 1-based destination page number.
            x (float): The left edge of the widget in PDF page coordinates.
            y (float): The bottom edge of the widget in PDF page coordinates.
            **kwargs: Optional `width`, `height`, `required`, and `tooltip`
                values.
        """
        super().__init__()
        self.hook_params = []

        self.page_number = page_number
        self.name = name
        self.x = x
        self.y = y
        self.optional_parameters = {
            each[0]: kwargs.get(each[0], each[1]) for each in self.OPTIONAL_PARAMS
        }
        for each in self.ALLOWED_HOOK_PARAMS:
            if each in kwargs:
                self.hook_params.append((each, kwargs.get(each)))

    @staticmethod
    def build_widget_watermarks(
        widgets: List[SignatureWidget],
        stream: bytes,
        annotation_builder: Callable[[PdfWriter, SignatureWidget], Any],
    ) -> List[bytes]:
        """
        Builds page-aligned carrier PDFs from widget annotation objects.

        Widgets are grouped by their 1-based page number. For every page that
        contains widgets, this method creates a blank, single-page PDF sized
        from the source page's media box. It asks ``annotation_builder`` to
        create each annotation and its dependent objects in that PDF's writer,
        then stores the returned annotation references in the page's `/Annots`
        array. Pages without widgets are represented by an empty byte string.

        Args:
            widgets (List[SignatureWidget]): Widgets to package into carrier PDFs.
            stream (bytes): Source PDF used to determine page count and page size.
            annotation_builder (Callable): Function that receives the destination
                writer and a widget, creates the annotation and its dependent
                objects, and returns the annotation object or reference.

        Returns:
            List[bytes]: Page-aligned PDF streams. Each non-empty entry is
            a single-page PDF containing the annotations for that source page.
        """
        page_to_widgets = defaultdict(list)
        for widget in widgets:
            page_to_widgets[widget.page_number].append(widget)

        input_pdf = PdfReader(BytesIO(stream))
        page_count = len(input_pdf.pages)
        result = [b""] * page_count

        for page_num in range(1, page_count + 1):
            page_widgets = page_to_widgets.get(page_num, [])
            if not page_widgets:
                continue

            watermark = BytesIO()
            page = input_pdf.pages[page_num - 1]
            canvas = Canvas(
                watermark,
                pagesize=(
                    float(page.mediabox[2]),
                    float(page.mediabox[3]),
                ),
            )
            canvas.showPage()
            canvas.save()
            watermark.seek(0)

            out = PdfWriter(watermark)
            annotations = [annotation_builder(out, widget) for widget in page_widgets]
            out.pages[0][NameObject(Annots)] = ArrayObject(  # pylint: disable=E1137
                annotations
            )

            with BytesIO() as result_stream:
                out.write(result_stream)
                result_stream.seek(0)
                result[page_num - 1] = result_stream.read()

        return result

    @staticmethod
    def bulk_watermarks(widgets: List[SignatureWidget], stream: bytes) -> List[bytes]:
        """
        Constructs signature widgets in page-aligned carrier PDFs.

        Each widget is represented by a `/Sig` annotation with a transparent
        interior and a dark-gray, one-point solid border. Its normal appearance
        stream contains only that border. The annotation and appearance are
        created in the carrier PDF's writer, so they do not retain references
        to another PDF. ``build_widget_watermarks`` then packages the
        annotations by source page.

        Args:
            widgets (List[SignatureWidget]): Signature widgets to construct.
            stream (bytes): Source PDF used to determine page count and page size.

        Returns:
            List[bytes]: Page-aligned PDF streams containing the constructed
            signature annotations.
        """

        def build_annotation(out: PdfWriter, widget: SignatureWidget) -> Any:
            width = float(widget.optional_parameters["width"])
            height = float(widget.optional_parameters["height"])
            border_color = (0.1, 0.1, 0.1)

            appearance = StreamObject()
            appearance.set_data(
                (
                    f"{border_color[0]:g} "
                    f"{border_color[1]:g} "
                    f"{border_color[2]:g} RG\n"
                    "1 w\n"
                    f"0.5 0.5 {width - 1:g} {height - 1:g} re\n"
                    "s\n"
                ).encode()
            )
            appearance.update(
                {
                    NameObject(PdfType): NameObject("/XObject"),
                    NameObject(Subtype): NameObject("/Form"),
                    NameObject("/BBox"): ArrayObject(
                        [
                            FloatObject(0),
                            FloatObject(0),
                            FloatObject(width),
                            FloatObject(height),
                        ]
                    ),
                    NameObject("/Resources"): DictionaryObject(),
                }
            )
            appearance_ref = out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
                appearance.flate_encode()
            )

            annotation = DictionaryObject(
                {
                    NameObject(PdfType): NameObject(Annot),
                    NameObject(Subtype): NameObject("/Widget"),
                    NameObject(Rect): ArrayObject(
                        [
                            FloatObject(widget.x),
                            FloatObject(widget.y),
                            FloatObject(widget.x + width),
                            FloatObject(widget.y + height),
                        ]
                    ),
                    NameObject("/MK"): DictionaryObject(
                        {
                            NameObject("/BC"): ArrayObject(
                                FloatObject(value) for value in border_color
                            )
                        }
                    ),
                    NameObject("/BS"): DictionaryObject(
                        {
                            NameObject(S): NameObject(S),
                            NameObject("/W"): NumberObject(1),
                        }
                    ),
                    NameObject(AP): DictionaryObject({NameObject(N): appearance_ref}),
                    NameObject(DA): TextStringObject("/Helv 0 Tf 0 g"),
                    NameObject(F): NumberObject(4),
                    NameObject(FT): NameObject(Sig),
                    NameObject("/H"): NameObject(N),
                    NameObject(T): TextStringObject(widget.name),
                    NameObject("/Q"): NumberObject(0),
                }
            )
            return out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
                annotation
            )

        return SignatureWidget.build_widget_watermarks(
            widgets, stream, build_annotation
        )


@dataclass
class SignatureField(Field):
    """
    Represents a signature field in a PDF document.

    This dataclass extends the `Field` base class and defines the specific
    dimensions that can be configured for a signature input field.

    Attributes:
        _widget_class (Type[SignatureWidget]): The widget class associated with this field type.
        width (Optional[float]): The width of the signature field.
        height (Optional[float]): The height of the signature field.
    """

    _widget_class: Type[SignatureWidget] = SignatureWidget

    width: Optional[float] = None
    height: Optional[float] = None
