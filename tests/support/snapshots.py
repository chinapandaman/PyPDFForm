# -*- coding: utf-8 -*-

import os

from PyPDFForm import Fields, PdfWrapper
from tests.support.checks import assert_same_pdf

# the user property naming an expected PDF that a test owns; reports carry it
# from pytest-xdist workers to the controller, which sees every owner
OWNED = "expected_pdf"


class ExpectPdf:
    # compares a test's output with an expected PDF, and records the output to
    # write when expected PDFs are regenerated

    def __init__(self, node, root, standard_zlib):
        super().__init__()
        self.node = node
        self.root = root
        self.standard_zlib = standard_zlib
        # the outputs to regenerate, by the path of their expected PDF
        self.outputs = {}
        # the outputs that differ from an expected PDF compared with same_as,
        # which a comparison run shows without regenerating that PDF
        self.mismatches = {}

    def __call__(
        self, stream, path=None, *, same_as=None, timestamped=False, length_only=False
    ):
        # path is the expected PDF this test owns and regenerates; same_as is
        # only compared, for example one that another test owns
        if length_only and same_as is None:
            msg = "length_only only applies to same_as"
            raise TypeError(msg)
        if path is not None and same_as is None:
            expected_path = os.path.abspath(path)
            owned = os.path.relpath(expected_path, self.root).replace(os.sep, "/")
            self.node.user_properties.append((OWNED, owned))
            # recorded before comparing, so that a failing test is regenerated
            self.outputs[expected_path] = stream
        elif path is None and same_as is not None:
            expected_path = os.path.abspath(same_as)
        else:
            msg = "expect_pdf takes either path or same_as"
            raise TypeError(msg)

        with open(expected_path, "rb") as f:
            expected = f.read()

        try:
            if length_only:
                # the objects differ, for example because they are numbered
                # differently
                if self.standard_zlib:
                    assert len(stream) == len(expected)
            else:
                assert_same_pdf(stream, expected, self.standard_zlib, timestamped)
        except Exception:
            if path is None:
                self.mismatches[expected_path] = stream
            raise

        if timestamped and path is not None:
            # a timestamped PDF is regenerated only when it changed
            del self.outputs[expected_path]


def run_sample_template_library_test(
    pdf_samples,
    image_samples,
    sample_font_stream,
    expect_pdf,
    generate_appearance_streams=False,
    need_appearances=False,
):
    subdir = (
        "generate_appearance_streams"
        if generate_appearance_streams
        else "need_appearances"
    )
    expected_path = os.path.join(
        pdf_samples, subdir, "test_sample_template_library.pdf"
    )

    obj = (
        PdfWrapper(
            os.path.join(pdf_samples, "dummy.pdf"),
            generate_appearance_streams=generate_appearance_streams,
            need_appearances=need_appearances,
        )
        .register_font("new_font", sample_font_stream)
        .bulk_create_fields(
            [
                Fields.TextField(
                    name="new_text_field_widget",
                    page_number=1,
                    x=60,
                    y=710,
                ),
                Fields.CheckBoxField(
                    name="new_checkbox_widget",
                    page_number=1,
                    x=100,
                    y=600,
                ),
                Fields.RadioGroup(
                    name="new_radio_group",
                    page_number=1,
                    x=[50, 100, 150],
                    y=[50, 100, 150],
                ),
                Fields.DropdownField(
                    name="new_dropdown_widget",
                    page_number=1,
                    x=300,
                    y=710,
                    options=[
                        "foo",
                        "bar",
                        "foobar",
                    ],
                    font="new_font",
                ),
                Fields.ImageField(
                    name="new_image_widget",
                    page_number=1,
                    x=300,
                    y=200,
                ),
                Fields.SignatureField(
                    name="new_signature_wiget",
                    page_number=1,
                    x=300,
                    y=400,
                ),
            ]
        )
        .fill(
            {
                "new_text_field_widget": "test text",
                "new_checkbox_widget": True,
                "new_radio_group": 1,
                "new_dropdown_widget": "barfoo",
                "new_image_widget": os.path.join(image_samples, "sample_image.jpg"),
                "new_signature_wiget": os.path.join(
                    image_samples, "sample_signature.png"
                ),
            },
        )
    )

    obj.widgets["new_text_field_widget"].font = "new_font"
    obj.widgets["new_text_field_widget"].font_color = (1, 0, 0)

    # Currently alignment is not respected due to qpdf limitations
    # https://github.com/qpdf/qpdf/blob/503d401615a842f7c5220a3ee425f5db2f25f537/TODO.md#text-appearance-streams
    obj.widgets["new_text_field_widget"].alignment = 2

    obj.widgets["new_checkbox_widget"].size = 40
    obj.widgets["new_radio_group"].size = 50

    expect_pdf(obj.read(), expected_path)
