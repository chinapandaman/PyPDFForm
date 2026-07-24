# -*- coding: utf-8 -*-
# pylint: disable=R0801
"""
This module defines the `ImageField` and `ImageWidget` classes, which are used
to represent and manipulate image form fields within PDF documents.

The `ImageField` class is a dataclass that encapsulates the properties of an
image field, inheriting from `SignatureField` for its dimensional attributes.

The `ImageWidget` class extends the base `SignatureWidget` class to provide
image-field annotation construction while reusing its placement and watermark
packaging infrastructure.
"""

from dataclasses import dataclass
from typing import Any, List, Type

from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
    StreamObject,
    TextStringObject,
)

from ..constants import (
    AP,
    DA,
    FT,
    IMAGE_FIELD_IDENTIFIER,
    JS,
    A,
    Action,
    Annot,
    Btn,
    D,
    F,
    Ff,
    JavaScript,
    N,
    Rect,
    S,
    Subtype,
    T,
)
from ..constants import Type as PdfType
from .signature import SignatureField, SignatureWidget


class ImageWidget(SignatureWidget):
    """
    Represents an image widget in a PDF form.

    This class inherits from the SignatureWidget and is specifically designed
    for creating image fields in PDF forms. It reuses the signature widget's
    placement parameters while constructing a push-button annotation with an
    image-import action.
    """

    @staticmethod
    def bulk_watermarks(widgets: List[SignatureWidget], stream: bytes) -> List[bytes]:
        """
        Constructs image widgets in page-aligned watermark PDFs.

        Each image field is built as a push-button annotation whose JavaScript
        action opens the PDF viewer's image-import dialog. Its normal, rollover,
        and pressed appearances have a transparent interior and use the same
        dark-gray, one-point border as a default text field.
        ``build_widget_watermarks`` packages the resulting annotations by source
        page.

        Args:
            widgets (List[SignatureWidget]): Image widgets to construct.
            stream (bytes): Source PDF used to determine page count and dimensions.

        Returns:
            List[bytes]: Page-aligned watermark streams containing the constructed
            image annotations.
        """

        def build_annotation(out: PdfWriter, widget: SignatureWidget) -> Any:
            width = float(widget.optional_parameters["width"])
            height = float(widget.optional_parameters["height"])
            border_color = (0.1, 0.1, 0.1)

            def build_appearance():
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
                        NameObject("/Matrix"): ArrayObject(
                            [
                                FloatObject(1),
                                FloatObject(0),
                                FloatObject(0),
                                FloatObject(1),
                                FloatObject(0),
                                FloatObject(0),
                            ]
                        ),
                    }
                )
                return out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
                    appearance.flate_encode()
                )

            appearance = build_appearance()

            annotation = DictionaryObject(
                {
                    NameObject(FT): NameObject(Btn),
                    NameObject(Ff): NumberObject(1 << 16),
                    NameObject(PdfType): NameObject(Annot),
                    NameObject(Subtype): NameObject("/Widget"),
                    NameObject(F): NumberObject(4),
                    NameObject("/MK"): DictionaryObject(
                        {
                            NameObject("/TP"): NumberObject(1),
                            NameObject("/IF"): DictionaryObject(
                                {NameObject(S): NameObject(A)}
                            ),
                            NameObject("/BC"): ArrayObject(
                                FloatObject(value) for value in border_color
                            ),
                        }
                    ),
                    NameObject("/BS"): DictionaryObject(
                        {
                            NameObject(S): NameObject(S),
                            NameObject("/W"): NumberObject(1),
                        }
                    ),
                    NameObject(A): DictionaryObject(
                        {
                            NameObject(PdfType): NameObject(Action),
                            NameObject(S): NameObject(JavaScript),
                            NameObject(JS): TextStringObject(IMAGE_FIELD_IDENTIFIER),
                        }
                    ),
                    NameObject(DA): TextStringObject("/Micr 12 Tf 0 0 0 rg"),
                    NameObject(Rect): ArrayObject(
                        [
                            FloatObject(widget.x),
                            FloatObject(widget.y),
                            FloatObject(widget.x + width),
                            FloatObject(widget.y + height),
                        ]
                    ),
                    NameObject(AP): DictionaryObject(
                        {
                            NameObject(N): appearance,
                            NameObject("/R"): appearance,
                            NameObject(D): appearance,
                        }
                    ),
                    NameObject(T): TextStringObject(widget.name),
                }
            )
            return out._add_object(  # type: ignore # noqa: SLF001 # pylint: disable=W0212
                annotation
            )

        return ImageWidget.build_widget_watermarks(widgets, stream, build_annotation)


@dataclass
class ImageField(SignatureField):
    """
    Represents an image field in a PDF document.

    This dataclass extends the `SignatureField` base class and defines an image
    input field. It inherits `width` and `height` from `SignatureField` because
    image and signature placeholders share the same sizing model.

    Attributes:
        _widget_class (Type[ImageWidget]): The widget class associated with this field type.
    """

    _widget_class: Type[ImageWidget] = ImageWidget
