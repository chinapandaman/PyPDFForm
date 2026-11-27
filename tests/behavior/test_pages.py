# -*- coding: utf-8 -*-

import re
from io import BytesIO

import pytest
from pikepdf import Array, Dictionary, Name, Pdf, Stream, String
from reportlab.pdfgen.canvas import Canvas

from PyPDFForm import BlankPage, Fields, PdfArray, PdfWrapper, RawElements
from tests.support.builders import build_cross_page_form, with_null_entry
from tests.support.checks import get_retained_content, get_values


def test_pages_inherit_attributes(template_stream):
    obj = PdfWrapper(
        template_stream,
        use_full_widget_name=True,
    )

    for page in obj.pages:
        assert getattr(page, "use_full_widget_name")


def test_blank_page():
    obj = PdfWrapper(BlankPage() * 1)
    # reading the PDF adds no widgets or pages
    obj.read()

    assert not obj.widgets
    assert len(obj.pages) == 1


def test_blank_page_custom_size_multiply():
    obj = PdfWrapper(BlankPage(595.35, 841.995) * 3)
    # reading the PDF adds no widgets or pages
    obj.read()

    assert not obj.widgets
    assert len(obj.pages) == 3


def test_pages_exclude_other_page_content(assert_page_ownership):
    buffer = BytesIO()
    canvas = Canvas(buffer)
    canvas.drawString(30, 700, "KEEP_FIRST_PAGE")
    canvas.acroForm.textfield(name="field1", x=30, y=600, width=100, height=20)
    canvas.showPage()
    canvas.drawString(30, 700, "EXCLUDED_SECRET_SECOND_PAGE")
    canvas.showPage()
    canvas.save()

    output = PdfWrapper(buffer.getvalue()).pages[0].read()

    assert get_retained_content(
        output, ["KEEP_FIRST_PAGE", "EXCLUDED_SECRET_SECOND_PAGE"]
    ) == {"KEEP_FIRST_PAGE"}
    assert_page_ownership(output)
    with Pdf.open(BytesIO(output)) as pdf:
        assert len(pdf.pages) == 1
        widget = pdf.pages[0].Annots[0]
        assert widget.P.objgen == pdf.pages[0].obj.objgen
        assert widget.P.Parent.Count == 1
    assert PdfWrapper(output).widgets.keys() == {"field1"}


def test_pages_keep_only_own_part_of_cross_page_fields(assert_page_ownership):
    pages = PdfWrapper(build_cross_page_form()).pages
    page_1_markers = ["KEEP_PAGE_1", "KEEP_NAME", "radio_a"]
    page_2_markers = [
        "SECRET_PAGE_2",
        "SECRET_IMAGE",
        "SECRET_SHARED_AP",
        "SECRET_ADDRESS",
        "SECRET_SOLO",
    ]
    page_3_markers = ["SECRET_RADIO_AP"]
    markers = page_1_markers + page_2_markers + page_3_markers
    first = pages[0].read()
    second = pages[1].read()

    for selection, expected in (
        (pages[0], page_1_markers),
        (pages[1], page_2_markers),
        (pages[2], page_3_markers),
        (pages[0:2], page_1_markers + page_2_markers),
        (PdfArray([pages[0], pages[2]]).merge(), page_1_markers + page_3_markers),
    ):
        stream = selection.read()
        assert get_retained_content(stream, markers) == set(expected)
        assert_page_ownership(stream)
        assert_page_ownership(PdfWrapper(stream).fill({}).read())

    assert PdfWrapper(first).data == {
        "shared": "shared_value",
        "name": "KEEP_NAME",
        "radio": None,
    }
    assert PdfWrapper(second).data == {
        "shared": "shared_value",
        "address": "SECRET_ADDRESS",
        "solo": "SECRET_SOLO",
    }
    with Pdf.open(BytesIO(first)) as pdf:
        page = pdf.pages[0].obj
        assert "/O" not in page.AA
        assert [str(annot.Subtype) for annot in page.Annots] == [
            "/Widget",
            "/Widget",
            "/Widget",
            "/Text",
            "/Popup",
            "/Widget",
            "/Widget",
            "/Widget",
        ]
        shared, name, radio, note, popup, goto_next, goto_last, goto_top = page.Annots
        for kid in (shared, name, radio):
            assert [each.objgen for each in kid.Parent.Kids] == [kid.objgen]
        assert "/A" not in goto_next
        assert list(goto_last.AA.keys()) == ["/D"]
        assert goto_last.AA.D.D[0].objgen == page.objgen
        assert goto_top.A.D[0].objgen == page.objgen
        assert note.Popup.objgen == popup.objgen
        assert popup.Parent.objgen == note.objgen


@pytest.mark.parametrize(
    ("key", "get_value", "path"),
    [
        (
            "/A",
            lambda pdf: Dictionary(
                S=Name.ResetForm, Fields=[pdf.Root.AcroForm.Fields[2]]
            ),
            "/A/Fields[0]",
        ),
        ("/A", lambda pdf: Dictionary(S=Name.Hide, T=pdf.pages[1].Annots[0]), "/A/T"),
        ("/IRT", lambda pdf: pdf.pages[2].Annots[0], "/IRT"),
        (
            "/A",
            lambda _: Dictionary(
                S=Name.ResetForm, Fields=["person.name", "person.address"]
            ),
            "/A/Fields[1]",
        ),
        (
            "/A",
            lambda _: Dictionary(
                S=Name.SubmitForm, F="https://example.com", Fields=["contact"]
            ),
            "/A/Fields[0]",
        ),
        ("/A", lambda _: Dictionary(S=Name.Hide, T="person.address"), "/A/T"),
        ("/A", lambda _: Dictionary(S=Name.Hide, T=["contact.solo"]), "/A/T[0]"),
        (
            "/A",
            lambda pdf: Dictionary(
                S=Name.ResetForm,
                Fields=[pdf.make_indirect(String("person.address"))],
            ),
            "/A/Fields[0]",
        ),
        (
            "/A",
            lambda pdf: Dictionary(
                S=Name.Hide, T=[pdf.make_indirect(String("contact"))]
            ),
            "/A/T[0]",
        ),
    ],
)
def test_pages_reject_other_cross_page_references(
    key, get_value, path, assert_page_ownership
):
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        pdf.pages[0].Annots[7][key] = get_value(pdf)
        stream = BytesIO()
        pdf.save(stream)

    form = PdfWrapper(stream.getvalue())
    with pytest.raises(
        ValueError,
        match=rf"Cannot copy page 1: /Annots\[7\]{re.escape(path)} refers to content "
        "that is not being copied",
    ):
        form.pages  # noqa: B018 # pylint: disable=W0104

    assert_page_ownership(form.draw([RawElements.RawText("drawn", 1, 100, 100)]).read())


@pytest.mark.parametrize("targets", ["shared", "copied", None])
def test_pages_check_targets_sharing_pruned_kids(targets):
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        person = pdf.Root.AcroForm.Fields[1]
        person.Kids = pdf.make_indirect(Array(person.Kids))
        if targets:
            pdf.pages[0].Annots[7].A = Dictionary(
                S=Name.ResetForm,
                Fields=person.Kids if targets == "shared" else Array(person.Kids),
            )
        stream = BytesIO()
        pdf.save(stream)

    form = PdfWrapper(stream.getvalue())
    if targets:
        with pytest.raises(
            ValueError,
            match=r"Cannot copy page 1: /Annots\[7\]/A/Fields\[1\] refers to "
            "content that is not being copied",
        ):
            form.pages  # noqa: B018 # pylint: disable=W0104
        return

    with Pdf.open(BytesIO(form.pages[0].read())) as pdf:
        name = next(a for a in pdf.pages[0].Annots if a.get("/T") == "name")
        assert [str(kid.T) for kid in name.Parent.Kids] == ["name"]


def test_pages_keep_actions_naming_copied_fields():
    names = ["person", "person.name", "shared", "unknown"]
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        pdf.pages[0].Annots[7].A = Dictionary(S=Name.ResetForm, Fields=names)
        stream = BytesIO()
        pdf.save(stream)

    with Pdf.open(BytesIO(PdfWrapper(stream.getvalue()).pages[0].read())) as pdf:
        assert [str(name) for name in pdf.pages[0].Annots[7].A.Fields] == names


def test_pages_reject_target_below_field_with_null_name():
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        # "person" gets a null name, so its kid on page 2 is named "address"
        pdf.pages[0].Annots[7].A = Dictionary(S=Name.Hide, T="address")
        stream = BytesIO()
        pdf.save(stream)

    form = PdfWrapper(with_null_entry(stream.getvalue(), "person", "/T"))
    with pytest.raises(
        ValueError,
        match=r"Cannot copy page 1: /Annots\[7\]/A/T refers to content that is "
        "not being copied",
    ):
        form.pages  # noqa: B018 # pylint: disable=W0104


def test_pages_split_radio_field_with_null_options():
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        # "radio" inherits its options from "group", past its own null /Opt
        radio = pdf.Root.AcroForm.Fields[3]
        group = pdf.make_indirect(
            Dictionary(T="group", Kids=[radio], Opt=["FIRST", "THIRD"])
        )
        radio.Parent = group
        radio.Opt = ["placeholder"]
        pdf.Root.AcroForm.Fields[3] = group
        stream = BytesIO()
        pdf.save(stream)

    pages = PdfWrapper(with_null_entry(stream.getvalue(), "radio", "/Opt")).pages
    with Pdf.open(BytesIO(pages[0].read())) as pdf:
        radio = next(
            annot.Parent
            for annot in pdf.pages[0].Annots
            if annot.get("/Parent", {}).get("/T") == "radio"
        )
        assert len(radio.Kids) == 1
        assert [str(each) for each in radio.Opt] == ["FIRST"]


def test_pages_renumber_positional_radio_states():
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        radio = pdf.Root.AcroForm.Fields[3]
        radio.Opt = ["FIRST_EXPORT", "THIRD_EXPORT"]
        radio.V = Name("/1")
        for index, kid in enumerate(radio.Kids):
            state = f"/{index}"
            on = next(iter(kid.AP.N.values()))
            kid.AP = Dictionary(
                N=Dictionary({state: on}), D=Dictionary({state: on}), R=on
            )
            kid.AS = Name(state) if index else Name.Off
        # A choice field whose options happen to match its two widgets.
        choice = pdf.make_indirect(
            Dictionary(FT=Name.Ch, Ff=131072, T="choice", Opt=["x", "y"], V="y")
        )
        choice.Kids = [
            pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Widget,
                    Rect=[10, 170, 110, 190],
                    P=page.obj,
                    Parent=choice,
                )
            )
            for page in pdf.pages[:2]
        ]
        for page, kid in zip(pdf.pages[:2], choice.Kids, strict=True):
            page.Annots.append(kid)
        pdf.Root.AcroForm.Fields.append(choice)
        stream = BytesIO()
        pdf.save(stream)
    template = stream.getvalue()

    def get_radio(output):
        pdf = Pdf.open(BytesIO(output))
        kid = next(
            annot
            for annot in pdf.pages[0].Annots
            if annot.get("/Parent", {}).get("/T") == "radio"
        )
        return pdf, kid.Parent, kid

    pages = PdfWrapper(template).pages
    for index, export, state, value, default in (
        (0, "FIRST_EXPORT", "/Off", None, None),
        (2, "THIRD_EXPORT", "/0", "/0", None),
    ):
        pdf, radio, kid = get_radio(pages[index].read())
        with pdf:
            assert [str(each) for each in radio.Opt] == [export]
            assert len(radio.Kids) == 1
            assert str(kid.AS) == state
            assert list(kid.AP.N.keys()) == list(kid.AP.D.keys()) == ["/0"]
            assert isinstance(kid.AP.R, Stream)
            assert get_values(radio) == (value, default)
    assert PdfWrapper(pages[0].read()).data["radio"] is None
    assert PdfWrapper(pages[2].read()).data["radio"] == 0

    with Pdf.open(BytesIO(pages[0].read())) as pdf:
        choice = next(
            annot.Parent
            for annot in pdf.pages[0].Annots
            if annot.get("/Parent", {}).get("/T") == "choice"
        )
        assert len(choice.Kids) == 1
        assert [str(each) for each in choice.Opt] == ["x", "y"]

    pdf, radio, kid = get_radio(PdfWrapper(template).draw([]).read())
    with pdf:
        assert [str(each) for each in radio.Opt] == ["FIRST_EXPORT", "THIRD_EXPORT"]
        assert [str(each.AS) for each in radio.Kids] == ["/Off", "/1"]
        assert get_values(radio) == ("/1", None)


def test_pages_renumber_shared_and_inherited_radio_states():
    with Pdf.open(BytesIO(build_cross_page_form())) as pdf:
        page_1, _, page_3 = pdf.pages
        radio = pdf.Root.AcroForm.Fields[3]
        on = next(iter(radio.Kids[0].AP.N.values()))
        for page in (page_1, page_3):
            page.obj.Annots = [
                annot
                for annot in page.Annots
                if annot.get("/Parent", {}).get("/T") != "radio"
            ]

        def widget(page, x, parent, appearances, state=Name.Off):
            kid = pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Widget,
                    Rect=[x, 130, x + 10, 140],
                    P=page.obj,
                    Parent=parent,
                    AP=appearances,
                    AS=state,
                )
            )
            page.Annots.append(kid)
            return kid

        shared = pdf.make_indirect(Dictionary({"/2": on, "/Off": on}))
        radio.Kids = [
            widget(page_3, 10, radio, Dictionary(N=Dictionary({"/0": on}))),
            widget(
                page_1,
                10,
                radio,
                Dictionary(N=Dictionary({"/1": on}), R=Dictionary({"/1": on})),
            ),
            widget(page_1, 40, radio, Dictionary(N=shared, D=shared), Name("/2")),
        ]
        radio.DV = Name("/0")
        del radio.V
        # /Opt and /V are inherited from a parent whose kids are radio groups.
        others = [
            pdf.make_indirect(Dictionary(FT=Name.Btn, Ff=49152, T=name))
            for name in ("other", "other_2")
        ]
        for x, other in zip((60, 90), others, strict=True):
            other.Kids = [
                widget(page_3, x, other, Dictionary(N=Dictionary({"/0": on})))
            ]
        group = pdf.make_indirect(
            Dictionary(
                T="group",
                FT=Name.Btn,
                Opt=["A", "B", "C"],
                V=Name("/2"),
                Kids=[radio, *others],
            )
        )
        for kid in group.Kids:
            kid.Parent = group
        pdf.Root.AcroForm.Fields[3] = group
        pdf.Root.AcroForm.Fields.extend(others)
        stream = BytesIO()
        pdf.save(stream)

    pages = PdfWrapper(stream.getvalue()).pages
    for index, options, value, default, kids in (
        (0, ["B", "C"], "/1", None, [("/Off", "/0"), ("/1", "/1")]),
        (2, ["A"], "/Off", "/0", [("/Off", "/0")]),
    ):
        output = pages[index].read()
        with Pdf.open(BytesIO(output)) as pdf:
            widgets = [
                annot
                for annot in pdf.pages[0].Annots
                if annot.get("/Parent", {}).get("/T") == "radio"
            ]
            radio = widgets[0].Parent
            assert [str(each) for each in radio.Opt] == options
            assert get_values(radio) == (value, default)
            assert [str(each) for each in radio.Parent.Opt] == ["A", "B", "C"]
            assert get_values(radio.Parent) == ("/2", None)
            assert len(radio.Parent.Kids) == (1 if index == 0 else 3)
            assert [
                (str(kid.AS), sorted(set(kid.AP.N.keys()) - {"/Off"})[0])
                for kid in widgets
            ] == kids
            if index == 0:
                first, second = widgets
                assert list(first.AP.R.keys()) == ["/0"]
                assert sorted(second.AP.N.keys()) == sorted(second.AP.D.keys())
                assert sorted(second.AP.N.keys()) == ["/1", "/Off"]
                assert second.AP.N["/1"].objgen == second.AP.D["/1"].objgen
        assert PdfWrapper(output).data["radio"] == (1 if index == 0 else None)


def test_pages_renumber_without_changing_other_fields():
    pdf = Pdf.new()
    for _ in range(2):
        pdf.add_blank_page()
    page_1, page_2 = (page.obj for page in pdf.pages)

    def appearance(text):
        return pdf.make_stream(
            text, Type=Name.XObject, Subtype=Name.Form, BBox=[0, 0, 10, 10]
        )

    off = appearance(b"off")
    # Both groups' selected buttons use one normal state dictionary.
    shared = pdf.make_indirect(Dictionary({"/1": appearance(b"on_1"), "/Off": off}))
    fields = []
    for y, name, pages in (
        (10, "split", (page_1, page_2)),
        (50, "kept", (page_2,) * 2),
    ):
        field = pdf.make_indirect(
            Dictionary(FT=Name.Btn, Ff=49152, T=name, Opt=["a", "b"], V=Name("/1"))
        )
        field.Kids = []
        for index, page in enumerate(pages):
            kid = pdf.make_indirect(
                Dictionary(
                    Type=Name.Annot,
                    Subtype=Name.Widget,
                    Rect=[10 + 20 * index, y, 20 + 20 * index, y + 10],
                    P=page,
                    Parent=field,
                    AP=Dictionary(
                        N=shared
                        if index
                        else Dictionary({"/0": appearance(b"on_0"), "/Off": off})
                    ),
                    AS=Name("/1") if index else Name.Off,
                )
            )
            if "/Annots" not in page:
                page.Annots = pdf.make_indirect([])
            page.Annots.append(kid)
            field.Kids.append(kid)
        fields.append(field)
    pdf.Root.AcroForm = Dictionary(Fields=fields)
    stream = BytesIO()
    pdf.save(stream)

    form = PdfWrapper(stream.getvalue())
    assert form.data == {"split": 1, "kept": 1}
    output = form.pages[1].read()
    assert PdfWrapper(output).data == {"split": 0, "kept": 1}
    with Pdf.open(BytesIO(output)) as pdf:
        split, kept = (
            [annot for annot in pdf.pages[0].Annots if str(annot.Parent.T) == name]
            for name in ("split", "kept")
        )
        assert [str(each) for each in split[0].Parent.Opt] == ["b"]
        assert (str(split[0].AS), sorted(split[0].AP.N.keys())) == (
            "/0",
            ["/0", "/Off"],
        )
        assert [str(each) for each in kept[0].Parent.Opt] == ["a", "b"]
        assert (str(kept[1].AS), sorted(kept[1].AP.N.keys())) == (
            "/1",
            ["/1", "/Off"],
        )
        assert split[0].AP.N["/0"].objgen == kept[1].AP.N["/1"].objgen


def test_clone_paths_keep_page_ownership(
    assert_page_ownership, assert_annotations_preserved
):
    template = build_cross_page_form(page_action=False)
    merged = PdfWrapper(template) + PdfWrapper(template)
    for result in (
        PdfWrapper(template).draw([RawElements.RawText("drawn", 1, 100, 100)]),
        PdfWrapper(template).generate_coordinate_grid(),
        merged,
        PdfWrapper(template).bulk_create_fields([Fields.TextField("new", 3, 10, 10)]),
    ):
        stream = result.read()
        assert_page_ownership(stream)
        if result is not merged:
            assert_annotations_preserved(template, stream, changed={"new"})
        with Pdf.open(BytesIO(stream)) as pdf:
            page_1, page_2, page_3 = (page.obj for page in pdf.pages[:3])
            shared, name, radio, _, _, goto_next, goto_last, _, _ = page_1.Annots
            for kid in (shared, name, radio):
                assert len(kid.Parent.Kids) == 2
            assert goto_next.A.D[0].objgen == page_2.objgen
            assert goto_last.AA.U.D[0].objgen == page_3.objgen
