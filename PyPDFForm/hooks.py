# -*- coding: utf-8 -*-

from io import BytesIO
from typing import cast, BinaryIO
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject


def trigger_widget_hooks(
    pdf: BinaryIO,
    widgets: dict,
    use_full_widget_name: bool,
) -> bytes:
    from .constants import Annots
    from .template import get_widget_key

    pdf_file = PdfReader(pdf)
    out = PdfWriter()
    out.append(pdf_file)

    for page in out.pages:
        for annot in page.get(Annots, []):
            annot = cast(DictionaryObject, annot.get_object())
            key = get_widget_key(annot.get_object(), use_full_widget_name)

            widget = widgets.get(key)
            if widget is None or not widget.hooks_to_trigger:
                continue

            for hook in widget.hooks_to_trigger:
                globals()[hook[0]](annot, hook[1])

            widget.hooks_to_trigger = []

    with BytesIO() as f:
        out.write(f)
        f.seek(0)
        return f.read()


def update_text_field_font_size(annot: DictionaryObject, value: float) -> None:
    from .constants import Parent, DA, FONT_SIZE_IDENTIFIER

    if Parent in annot and DA not in annot:
        text_appearance = annot[Parent][DA]
    else:
        text_appearance = annot[DA]

    text_appearance = text_appearance.split(" ")
    font_size_index = 0
    for i, val in enumerate(text_appearance):
        if val.startswith(FONT_SIZE_IDENTIFIER):
            font_size_index = i - 1
            break

    text_appearance[font_size_index] = str(value)
    new_text_appearance = " ".join(text_appearance)

    if Parent in annot and DA not in annot:
        annot[NameObject(Parent)][NameObject(DA)] = TextStringObject(new_text_appearance)
    else:
        annot[NameObject(DA)] = TextStringObject(new_text_appearance)
