# -*- coding: utf-8 -*-

from io import BytesIO

import pytest
from pikepdf import Dictionary, Name, Pdf

from PyPDFForm import Annotations, PdfArray, PdfWrapper, RawElements
from tests.support.checks import get_link_targets


def test_link_page_destinations(template_stream):
    with Pdf.open(BytesIO(template_stream)) as pdf:
        # Links from another tool: a GoTo action and a link to its own page.
        pdf.pages[0].Annots.append(
            pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Link,
                    Rect=[0, 0, 10, 10],
                    BS=Dictionary(W=1, D=[3]),
                    A=Dictionary(
                        S=Name.GoTo, D=[pdf.pages[2].obj, Name.XYZ, 0, 500, 0]
                    ),
                )
            )
        )
        pdf.pages[1].Annots.append(
            pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Link,
                    Rect=[0, 0, 10, 10],
                    Dest=[pdf.pages[1].obj, Name.Fit],
                )
            )
        )
        stream = BytesIO()
        pdf.save(stream)

    linked = PdfWrapper(stream.getvalue()).annotate(
        [
            Annotations.LinkAnnotation(1, 70, 705, 95, 20, page=2),
            Annotations.LinkAnnotation(1, 70, 600, 95, 20, uri="https://example.com/"),
        ]
    )
    targets = [
        (1, 3, ["/XYZ", "0", "500", "0"]),
        (1, 2, ["/Fit"]),
        (1, "https://example.com/", []),
        (2, 2, ["/Fit"]),
    ]
    shifted = [
        (page + 3, target + 3 if isinstance(target, int) else target, view)
        for page, target, view in targets
    ]
    other = PdfWrapper(template_stream)
    merged = other + linked

    assert get_link_targets(linked.read()) == targets
    assert get_link_targets(merged.read()) == shifted
    assert get_link_targets((linked + other).read()) == targets
    assert get_link_targets(PdfArray([other, linked, other]).merge().read()) == shifted
    assert get_link_targets(PdfWrapper(merged.read()).pages[3].read()) == [
        (1, "https://example.com/", [])
    ]
    assert get_link_targets(linked.pages[1].read()) == [(1, 1, ["/Fit"])]
    with Pdf.open(BytesIO(merged.read())) as pdf:
        assert [
            list(annot.BS.D)
            for page in pdf.pages
            for annot in page.get("/Annots", [])
            if "/BS" in annot and "/D" in annot.BS
        ] == [[3]]

    for result in (
        PdfWrapper(linked.read()).draw([RawElements.RawText("drawn", 1, 100, 100)]),
        PdfWrapper(linked.read()).generate_coordinate_grid(),
    ):
        assert get_link_targets(result.read()) == targets
        assert get_link_targets(PdfWrapper(result.read()).read()) == targets


def test_invalid_link_page(template_stream):
    form = PdfWrapper(template_stream)
    stream = form.read()
    for page_number, page in ((1, 0), (1, 4), (9, 4)):
        with pytest.raises(
            ValueError, match=rf"Link page {page} must satisfy 1 <= page <= 3\."
        ):
            form.annotate(
                [
                    Annotations.TextAnnotation(1, 100, 100, contents="not added"),
                    Annotations.LinkAnnotation(page_number, 70, 705, 95, 20, page=page),
                ]
            )

        assert form.read() == stream
