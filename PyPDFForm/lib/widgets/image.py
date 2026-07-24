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
    A,
    AP,
    D,
    DA,
    F,
    FT,
    Ff,
    JS,
    N,
    S,
    Action,
    Annot,
    Btn,
    IMAGE_FIELD_IDENTIFIER,
    JavaScript,
    Rect,
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
        action opens the PDF viewer's image-import dialog. Normal, rollover, and
        pressed appearance streams are created in the destination writer, and
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

            def build_appearance(gray: float):
                appearance = StreamObject()
                appearance.set_data(
                    (
                        f"{gray:g} {gray:g} {gray:g} rg\n"
                        f"0 0 {width:g} {height:g} re\n"
                        "f\n"
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

            normal_appearance = build_appearance(0.501961)
            rollover_appearance = build_appearance(0.501961)
            down_appearance = build_appearance(0.498039)

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
                            NameObject("/BG"): ArrayObject(
                                [
                                    FloatObject(0.501961),
                                    FloatObject(0.501961),
                                    FloatObject(0.501961),
                                ]
                            ),
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
                            NameObject(N): normal_appearance,
                            NameObject("/R"): rollover_appearance,
                            NameObject(D): down_appearance,
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
