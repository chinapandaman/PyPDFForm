# -*- coding: utf-8 -*-

import os
from io import BytesIO

import pytest
from pypdf import PdfWriter
from pypdf.generic import ArrayObject, DictionaryObject, NameObject, TextStringObject
from reportlab.pdfbase.pdfmetrics import _fonts

from PyPDFForm import Annotations, BlankPage, Fields, PdfWrapper
from PyPDFForm.lib.constants import (
    DEFAULT_ASSUMED_GLYPH_WIDTH,
    DR,
    IMAGE_IMPORT_JAVASCRIPT,
    AcroForm,
    Font,
    FontDescriptor,
    MissingWidth,
    Widths,
)


@pytest.fixture
def pdf_samples():
    # the input PDFs; expected PDFs are in expected_pdfs
    return os.path.join(os.path.dirname(__file__), "..", "..", "pdf_samples", "input")


@pytest.fixture
def expected_pdfs():
    # for same_as, and for tests that read another test's expected PDF
    return os.path.join(
        os.path.dirname(__file__), "..", "..", "pdf_samples", "expected"
    )


@pytest.fixture
def js_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "js_samples")


@pytest.fixture
def json_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "json_samples")


@pytest.fixture
def yaml_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "yaml_samples")


@pytest.fixture
def static_pdfs():
    return os.path.join(os.path.dirname(__file__), "..", "..", "docs", "pdfs")


@pytest.fixture
def template_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_filled_stream(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template_filled.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def template_with_radiobutton_stream(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_radio_button.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def image_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "image_samples")


@pytest.fixture
def font_samples():
    return os.path.join(os.path.dirname(__file__), "..", "..", "font_samples")


@pytest.fixture
def sample_font_stream(font_samples):
    with open(os.path.join(font_samples, "LiberationSerif-BoldItalic.ttf"), "rb+") as f:
        return f.read()


@pytest.fixture
def data_dict():
    return {
        "test": "test_1",
        "check": True,
        "test_2": "test_2",
        "check_2": False,
        "test_3": "test_3",
        "check_3": True,
    }


@pytest.fixture
def sejda_template(pdf_samples):
    with open(os.path.join(pdf_samples, "sample_template_sejda.pdf"), "rb+") as f:
        return f.read()


@pytest.fixture
def sejda_template_complex(pdf_samples):
    with open(
        os.path.join(pdf_samples, "paragraph", "sample_template_sejda_complex.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_font_colors(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_font_colors.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_complex_fonts(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_complex_fonts.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_paragraph_complex(pdf_samples):
    with open(
        os.path.join(pdf_samples, "paragraph", "sample_template_paragraph_complex.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_paragraph_max_length(pdf_samples):
    with open(
        os.path.join(
            pdf_samples, "paragraph", "sample_template_with_paragraph_max_length.pdf"
        ),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_max_length_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_max_length_text_field.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_comb_text_field.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_comb_text_field_right_aligned(pdf_samples):
    with open(
        os.path.join(
            pdf_samples, "sample_template_with_comb_text_field_right_aligned.pdf"
        ),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_right_aligned_text_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_right_aligned_text_field.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_dropdown(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "sample_template_with_dropdown.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_image_field(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_image_field.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def sample_template_with_full_key(pdf_samples):
    with open(
        os.path.join(pdf_samples, "sample_template_with_full_key.pdf"), "rb+"
    ) as f:
        return f.read()


@pytest.fixture
def dropdown_alignment(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "dropdown_alignment.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def dropdown_alignment_sejda(pdf_samples):
    with open(
        os.path.join(pdf_samples, "dropdown", "dropdown_alignment_sejda.pdf"),
        "rb+",
    ) as f:
        return f.read()


@pytest.fixture
def sejda_data():
    return {
        "date": "01-01",
        "year": "21",
        "buyer_name": "John Doe",
        "buyer_address": "1 N Main St, Chicago, IL 60000",
        "seller_name": "Jack Smith",
        "seller_address": "2 S Main St, Chicago, IL 60000",
        "make": "AK",
        "model": "47",
        "caliber": "7.62-x39mm",
        "serial_number": "111111",
        "purchase_option": 0,
        "date_of_this_bill": True,
        "at_future_date": True,
        "other": True,
        "other_reason": "NO REASONS",
        "payment_amount": "400",
        "future_date": "01-01",
        "future_year": "22",
        "exchange_for": "Food",
        "buyer_name_printed": "John Doe",
        "seller_name_printed": "Jack Smith",
        "buyer_signed_date": "2021-01-01",
        "seller_signed_date": "2021-01-01",
        "buyer_dl_number": "D000-4609-0001",
        "seller_dl_number": "S530-4209-0001",
        "buyer_dl_state": "IL",
        "seller_dl_state": "IL",
    }


@pytest.fixture
def sejda_complex_data():
    return {
        "checkbox": True,
        "radio": 0,
        "dropdown_font_auto_left": 0,
        "dropdown_font_auto_center": 1,
        "dropdown_font_auto_right": 2,
        "dropdown_font_ten_left": 0,
        "dropdown_font_ten_center": 1,
        "dropdown_font_ten_right": 2,
        "paragraph_font_auto_left": "paragraph_font_auto_left",
        "paragraph_font_auto_center": "paragraph_font_auto_center",
        "paragraph_font_auto_right": "paragraph_font_auto_right",
        "paragraph_font_ten_left": "paragraph_font_ten_left",
        "paragraph_font_ten_center": "paragraph_font_ten_center",
        "paragraph_font_ten_right": "paragraph_font_ten_right",
        "text__font_auto_left": "test text left",
        "text_font_auto_center": "test text center",
        "text_font_auto_right": "test text right",
        "text_font_ten_left": "text_font_ten_left",
        "text_font_ten_center": "text_font_ten_center",
        "text_font_ten_right": "text_font_ten_right",
    }


@pytest.fixture(params=[False, True], ids=["short-names", "full-names"])
def annotated_form(request):
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    writer.add_blank_page(612, 792)
    fields = []
    for name, field_type, y in (
        ("first", "/Sig", 100),
        ("second", "/Sig", 200),
        ("image", "/Btn", 300),
        ("text", "/Tx", 400),
    ):
        properties = {
            "/Subtype": "/Widget",
            "/FT": field_type,
            "/T": TextStringObject(name),
            "/Rect": [40, y, 200, y + 50],
        }
        if name == "image":
            properties["/A"] = {
                "/S": "/JavaScript",
                "/JS": TextStringObject(IMAGE_IMPORT_JAVASCRIPT),
            }
        if name == "text":
            properties["/V"] = TextStringObject("retained value")
            properties["/DA"] = TextStringObject("/Helv 12 Tf 0 g")
        fields.append(writer.add_annotation(0, properties).indirect_reference)

    roots = ArrayObject(fields)
    if request.param:
        parent = writer._add_object(  # type: ignore # noqa: SLF001
            DictionaryObject(
                {
                    NameObject("/T"): TextStringObject("group"),
                    NameObject("/Kids"): roots,
                }
            )
        )
        for field in fields:
            field.get_object()[NameObject("/Parent")] = parent
        # The same short name under a different parent must remain untouched.
        other = writer.add_annotation(
            1,
            {
                "/Subtype": "/Widget",
                "/FT": "/Sig",
                "/T": TextStringObject("first"),
                "/Rect": [40, 100, 200, 150],
            },
        )
        other_parent = writer._add_object(  # type: ignore # noqa: SLF001
            DictionaryObject(
                {
                    NameObject("/T"): TextStringObject("other"),
                    NameObject("/Kids"): ArrayObject([other.indirect_reference]),
                }
            )
        )
        other[NameObject("/Parent")] = other_parent
        roots = ArrayObject([parent, other_parent])
    writer.root_object[NameObject("/AcroForm")] = DictionaryObject(
        {NameObject("/Fields"): roots}
    )

    note = writer.add_annotation(
        0,
        Annotations.TextAnnotation(
            1,
            300,
            400,
            contents="keep note",
            title="group.first" if request.param else "first",
        ).get_specific_properties(),
    )
    writer.add_annotation(
        0,
        {
            "/Subtype": "/Popup",
            "/Rect": [300, 400, 400, 500],
            "/Parent": note.indirect_reference,
        },
    )
    reply = writer.add_annotation(
        0,
        Annotations.TextAnnotation(
            1, 300, 450, contents="keep reply"
        ).get_specific_properties(),
    )
    reply[NameObject("/IRT")] = note.indirect_reference
    writer.add_annotation(
        0,
        {
            "/Subtype": "/Link",
            "/Rect": [300, 300, 400, 320],
            "/Dest": ArrayObject(
                [writer.pages[1].indirect_reference, NameObject("/Fit")]
            ),
        },
    )
    writer.add_annotation(
        0,
        Annotations.HighlightAnnotation(
            1, 300, 200, width=100, height=20
        ).get_specific_properties(),
    )
    writer.add_annotation(
        1,
        Annotations.TextAnnotation(
            2, 300, 400, contents="second page"
        ).get_specific_properties(),
    )
    if request.param:
        # Annotation arrays and field arrays may themselves be indirect objects.
        for page in writer.pages:
            page[NameObject("/Annots")] = writer._add_object(page.annotations)  # type: ignore # noqa: SLF001
        for reference in roots:
            parent = reference.get_object()
            parent[NameObject("/Kids")] = writer._add_object(parent["/Kids"])  # type: ignore # noqa: SLF001
        writer.root_object["/AcroForm"][NameObject("/Fields")] = writer._add_object(  # type: ignore # noqa: SLF001
            roots
        )
    stream = BytesIO()
    writer.write(stream)
    return PdfWrapper(stream.getvalue(), use_full_widget_name=request.param)


@pytest.fixture
def font_registry():
    original = dict(_fonts)
    yield _fonts
    # Restore shared state even when a regression assertion fails.
    _fonts.clear()
    _fonts.update(original)


@pytest.fixture
def pdf_font_widths_and_missing(static_pdfs, sample_font_stream):
    path = os.path.join(static_pdfs, "sample_template.pdf")
    obj = PdfWrapper(path, need_appearances=True)
    obj.register_font("new_font_name", sample_font_stream)

    writer = PdfWriter(BytesIO(obj.read()))
    fonts = writer._root_object[AcroForm][DR][Font]  # type: ignore # noqa: SLF001
    font_obj = fonts[obj._available_fonts["new_font_name"]].get_object()  # type: ignore # noqa: SLF001

    pdf_widths_array = font_obj.get(Widths, [])
    descriptor_obj = font_obj[FontDescriptor].get_object()
    missing_width = descriptor_obj.get(MissingWidth, DEFAULT_ASSUMED_GLYPH_WIDTH)

    return pdf_widths_array, missing_width


@pytest.fixture
def full_name_forms():
    return [
        PdfWrapper(BlankPage(), use_full_widget_name=True)
        .bulk_create_fields([Fields.TextField(name, 1, 100, 100)])
        .fill({name: f"{name} value"})
        for name in ("left", "right")
    ]
