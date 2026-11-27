# -*- coding: utf-8 -*-

from io import BytesIO
from unittest.mock import patch

import pytest
from pikepdf import Array, Dictionary, Name, ObjectStreamMode, Pdf, String
from pypdf import PdfReader, PdfWriter

from PyPDFForm import PdfWrapper
from tests.support.builders import (
    build_action,
    save,
    with_actions,
    with_catalog_extras,
)
from tests.support.checks import (
    describe_actions,
    describe_catalog,
    describe_removal,
    describe_targets,
    get_button,
    get_retained_content,
)


def test_remove_fields_update_widgets(template_stream):
    obj = PdfWrapper(template_stream)
    obj.remove_fields(["test", "test_2", "check_2"])

    assert "test" not in obj.widgets
    assert "test_2" not in obj.widgets
    assert "check_2" not in obj.widgets


def test_remove_fields_no_keys_specified(template_stream):
    assert (
        PdfWrapper(template_stream).remove_fields([]).widgets.keys()
        == PdfWrapper(template_stream).widgets.keys()
    )


def test_remove_fields_unknown_key_writes_once(template_stream):
    obj = PdfWrapper(template_stream)

    with patch("PyPDFForm.lib.field_tree.PdfWriter", wraps=PdfWriter) as writer:
        obj.remove_fields(["missing"])

    # nothing was detached, so the PDF isn't cloned a second time
    assert writer.call_count == 1
    assert obj.widgets.keys() == PdfWrapper(template_stream).widgets.keys()


@pytest.mark.parametrize(
    ("keys", "use_full_widget_name", "removed", "calculation_order"),
    [
        (["test"], False, {"test"}, ["group.test_2", "hidden_business_id"]),
        (["test_2"], False, {"group.test_2"}, ["test", "hidden_business_id"]),
        (["group.test_2"], True, {"group.test_2"}, ["test", "hidden_business_id"]),
        (
            ["test_2", "test_3"],
            False,
            {"group.test_2", "group.test_3"},
            ["test", "hidden_business_id"],
        ),
        (
            ["hidden_business_id"],
            False,
            {"hidden_business_id"},
            ["test", "group.test_2"],
        ),
        (
            ["submit_button"],
            False,
            {"submit_button"},
            ["test", "group.test_2", "hidden_business_id"],
        ),
        (
            [
                "test",
                "check",
                "test_2",
                "check_2",
                "test_3",
                "check_3",
                "submit_button",
                "hidden_business_id",
            ],
            False,
            None,
            [],
        ),
    ],
    ids=[
        "field",
        "child",
        "child_full_name",
        "all_children",
        "without_widget",
        "unsupported",
        "all",
    ],
)
def test_remove_fields_updates_catalog(
    template_stream,
    assert_catalog_fields,
    keys,
    use_full_widget_name,
    removed,
    calculation_order,
):
    stream = with_catalog_extras(template_stream)
    expected = describe_catalog(stream)
    removed = set(expected["fields"]) if removed is None else removed
    obj = PdfWrapper(stream, use_full_widget_name=use_full_widget_name)

    obj.remove_fields(keys)
    output = obj.read()
    result = describe_catalog(output)

    remaining = {
        name: value for name, value in expected["fields"].items() if name not in removed
    }
    assert result["fields"] == remaining
    # an emptied parent would be listed as a field without widgets
    assert_catalog_fields(output, list(remaining))
    assert result["calculation_order"] == calculation_order
    assert ("/CO" in result["entries"]) == bool(calculation_order)


def test_remove_fields_radio_group(
    template_with_radiobutton_stream, assert_catalog_fields
):
    obj = PdfWrapper(template_with_radiobutton_stream)
    expected = [key for key in obj.widgets if key != "radio_1"]

    obj.remove_fields(["radio_1"])

    assert list(obj.widgets) == expected
    assert_catalog_fields(obj.read(), expected)


def test_remove_fields_keeps_widget_references(template_stream, assert_catalog_fields):
    # widgets that stay on a page are the same objects as in the field tree
    obj = PdfWrapper(template_stream).remove_fields(["test"])

    assert_catalog_fields(
        obj.read(), ["check", "test_2", "check_2", "test_3", "check_3"]
    )


def test_remove_all_fields_removes_values(template_stream, assert_catalog_fields):
    obj = PdfWrapper(template_stream).fill({"test": "REVIEW_SENTINEL"})

    obj.remove_fields(list(obj.widgets))
    stream = obj.read()

    assert not obj.widgets
    assert_catalog_fields(stream, [])
    assert not PdfReader(BytesIO(stream)).get_fields()
    assert not PdfWrapper(stream).widgets
    # removed fields aren't kept as unreachable objects
    assert not get_retained_content(stream, ["REVIEW_SENTINEL"])


def test_remove_fields_without_widgets_on_pages(sejda_template):
    obj = PdfWrapper(sejda_template)
    widgets = list(obj.widgets)

    obj.remove_fields(["Date", "Buyers Name"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        names = [str(field.get("/T", "")) for field in pdf.Root.AcroForm.Fields]
    assert "Date" not in names
    assert "Buyers Name" not in names
    # other fields without widgets on pages are kept
    assert "Make" in names
    assert "date" in names
    assert list(obj.widgets) == widgets


@pytest.mark.parametrize(
    ("action", "keys", "use_full_widget_name", "expected"),
    [
        (("/ResetForm", 0, ["@test", "@check"]), ["test"], False, ["@check"]),
        (("/ResetForm", 0, ["@test"]), ["test"], False, None),
        (("/ResetForm", 0, ["test", "check"]), ["test"], False, ["check"]),
        (("/SubmitForm", 0, ["test"]), ["test"], False, None),
        (("/SubmitForm", 5, ["@test", "test"]), ["test"], False, []),
        (("/Hide", None, "@test"), ["test"], False, None),
        (("/Hide", None, ["@test", "check"]), ["test"], False, ["check"]),
        (("/Hide", None, "test"), ["check"], False, ["test"]),
        (
            ("/ResetForm", 0, ["group", "group.test_2", "@group", "@group.test_2"]),
            ["test_2"],
            False,
            ["group", "@group"],
        ),
        (
            ("/ResetForm", 0, ["group", "@group.test_3"]),
            ["test_2", "test_3"],
            False,
            None,
        ),
        (
            ("/ResetForm", 0, ["group.test_2", "test_2", "test"]),
            ["group.test_2"],
            True,
            ["test_2", "test"],
        ),
        (
            ("/ResetForm", 0, ["unknown", "@hidden_business_id"]),
            ["hidden_business_id"],
            False,
            ["unknown"],
        ),
    ],
    ids=[
        "reference",
        "only_reference",
        "name",
        "only_name",
        "exclude",
        "hide_reference",
        "hide_array",
        "hide_other_field",
        "parent_kept",
        "parent_removed",
        "full_name",
        "unknown_name",
    ],
)
def test_remove_fields_updates_action_targets(
    template_stream, action, keys, use_full_widget_name, expected
):
    kind, flags, targets = action
    key = "/T" if kind == "/Hide" else "/Fields"

    def add(pdf, fields):
        values = [
            fields[each[1:]] if each.startswith("@") else String(each)
            for each in (targets if isinstance(targets, list) else [targets])
        ]
        button = get_button(pdf)
        button.A = Dictionary(S=Name(kind))
        button.A[key] = Array(values) if isinstance(targets, list) else values[0]
        if flags is not None:
            button.A.Flags = flags

    obj = PdfWrapper(
        with_actions(template_stream, add), use_full_widget_name=use_full_widget_name
    )
    obj.remove_fields(keys)

    with Pdf.open(BytesIO(obj.read())) as pdf:
        result = get_button(pdf).get("/A")
        assert (result if result is None else describe_targets(result[key])) == (
            expected
        )


@pytest.mark.parametrize(
    ("keys", "expected"),
    [(["test_2"], ["@group.test_3"]), (["test_2", "test_3"], None)],
)
def test_remove_fields_action_targets_sharing_kids(template_stream, keys, expected):
    # removal empties /Kids in place, so an action whose /Fields is the same
    # array would otherwise act on every field
    def add(pdf, fields):
        fields["group"].Kids = pdf.make_indirect(Array(fields["group"].Kids))
        get_button(pdf).A = Dictionary(S=Name.ResetForm, Fields=fields["group"].Kids)

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(keys)

    with Pdf.open(BytesIO(obj.read())) as pdf:
        result = get_button(pdf).get("/A")
        assert (result if result is None else describe_targets(result.Fields)) == (
            expected
        )


def test_remove_fields_action_targets_kids_cycle(template_stream):
    # a field listed in its own /Kids
    def add(pdf, fields):
        fields["group"].Kids.append(fields["group"])
        get_button(pdf).A = Dictionary(
            S=Name.ResetForm, Fields=Array([String("group.test_2"), String("test")])
        )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test_2"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        assert describe_targets(get_button(pdf).A.Fields) == ["test"]


def test_remove_fields_removes_action_targets_from_output(template_stream):
    # a reset button naming test by reference kept the removed field and its
    # value in the output
    def add(pdf, fields):
        get_button(pdf).A = Dictionary(S=Name.ResetForm, Fields=Array([fields["test"]]))

    obj = PdfWrapper(with_actions(template_stream, add)).fill({"test": "SECRET"})
    obj.remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf, BytesIO() as f:
        assert "/A" not in get_button(pdf)
        # qpdf writes only the objects reachable from the trailer
        pdf.save(f, object_stream_mode=ObjectStreamMode.disable)
        assert b"SECRET" not in f.getvalue()


def test_remove_fields_updates_actions_everywhere(template_stream):
    # an action that only names test, followed by JavaScript, in each kind of
    # entry that holds actions, does nothing in place
    def add(pdf, fields):
        def action():
            return build_action(("reset", ("after", None)), fields["test"])

        button = get_button(pdf)
        button.A = action()
        button.AA = Dictionary(D=action())
        pdf.pages[0].obj.AA = Dictionary(O=action())
        pdf.pages[0].obj.PresSteps = Dictionary(
            Type=Name.NavNode, NA=action(), PA=action()
        )
        fields["group"].AA = Dictionary(K=action())
        pdf.Root.OpenAction = action()
        pdf.Root.AA = Dictionary(WC=action())
        outlines = pdf.make_indirect(Dictionary(Type=Name.Outlines, Count=1))
        item = pdf.make_indirect(
            Dictionary(Title=String("item"), Parent=outlines, A=action())
        )
        outlines.First = item
        outlines.Last = item
        pdf.Root.Outlines = outlines
        pdf.Root.Names = Dictionary(
            JavaScript=Dictionary(
                Names=Array(
                    [
                        String("document"),
                        Dictionary(
                            S=Name.JavaScript, JS=String("document"), Next=action()
                        ),
                    ]
                )
            )
        )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        button = get_button(pdf)
        group = next(
            field for field in pdf.Root.AcroForm.Fields if field.get("/T") == "group"
        )
        result = {
            "annotation": button.A,
            "annotation_trigger": button.AA.D,
            "page_trigger": pdf.pages[0].obj.AA.O,
            "navigation_forward": pdf.pages[0].obj.PresSteps.NA,
            "navigation_backward": pdf.pages[0].obj.PresSteps.PA,
            "field_trigger": group.AA.K,
            "open_action": pdf.Root.OpenAction,
            "catalog_trigger": pdf.Root.AA.WC,
            "outline": pdf.Root.Outlines.First.A,
            "named_javascript": pdf.Root.Names.JavaScript.Names[1],
        }
        assert {key: describe_actions(value) for key, value in result.items()} == {
            key: ["document", "/Hide", "after"]
            if key == "named_javascript"
            else ["/Hide", "after"]
            for key in result
        }


@pytest.mark.parametrize(
    ("a", "aa", "expected"),
    [
        (
            ("reset", [("one", ("two", None)), ("three", None)]),
            None,
            (["/Hide", "one", "two", "three"], None),
        ),
        (
            ("one", [("reset", ("two", None)), ("three", None)]),
            None,
            (["one", "/Hide", "two", "three"], None),
        ),
        (
            ("one", [("reset", ("reset", None)), ("two", None)]),
            None,
            (["one", "/Hide", "/Hide", "two"], None),
        ),
        (
            None,
            {"/D": ("reset", None), "/U": ("one", None)},
            ([], {"/U": ["one"]}),
        ),
    ],
    ids=["chain_after", "chain_inside", "stopped_chain", "trigger"],
)
def test_remove_fields_chains_with_stopped_actions(template_stream, a, aa, expected):
    # an action that names only test does nothing in place, and an entry whose
    # actions all do nothing is removed
    def add(pdf, fields):
        button = get_button(pdf)
        if a is not None:
            button.A = build_action(a, fields["test"])
        if aa is not None:
            button.AA = Dictionary(
                {
                    trigger: build_action(spec, fields["test"])
                    for trigger, spec in aa.items()
                }
            )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        button = get_button(pdf)
        assert (
            describe_actions(button.get("/A")),
            {
                str(trigger): describe_actions(action)
                for trigger, action in button.AA.items()
            }
            if "/AA" in button
            else None,
        ) == expected


def test_remove_fields_no_op_keeps_type_and_next(template_stream):
    def add(pdf, fields):
        get_button(pdf).A = Dictionary(
            Type=Name.Action,
            S=Name.SubmitForm,
            F=String("https://example.com/submit"),
            Flags=4,
            Fields=Array([fields["test"]]),
            Next=Dictionary(S=Name.JavaScript, JS=String("after")),
        )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        action = get_button(pdf).A
        assert sorted(action.keys()) == ["/Next", "/S", "/T", "/Type"]
        assert (action.Type, action.S, list(action.T)) == ("/Action", "/Hide", [])
        assert describe_actions(action.Next) == ["after"]


def test_remove_fields_shared_action_cycle(template_stream):
    # one action that stops acting, in two entries and followed by itself
    def add(pdf, fields):
        reset = pdf.make_indirect(build_action(("reset", None), fields["test"]))
        reset.Next = reset
        button = get_button(pdf)
        button.A = Dictionary(S=Name.JavaScript, JS=String("one"), Next=reset)
        button.AA = Dictionary(D=reset)

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        button = get_button(pdf)
        assert describe_actions(button.A) == ["one", "/Hide", "again"]
        assert "/AA" not in button


def test_remove_fields_mutual_action_cycle(template_stream):
    # actions that stop acting and follow each other, each followed by one
    # that keeps acting
    def add(pdf, fields):
        first, second = (
            pdf.make_indirect(build_action(("reset", None), fields["test"]))
            for _ in range(2)
        )
        first.Next = Array([second, Dictionary(S=Name.JavaScript, JS=String("x"))])
        second.Next = Array([first, Dictionary(S=Name.JavaScript, JS=String("y"))])
        get_button(pdf).A = first

    expected, result = describe_removal(
        template_stream, add, lambda pdf: get_button(pdf).A
    )

    assert expected == ["/Hide", "/Hide", "again", "y", "x"]
    assert result == expected


def test_remove_fields_cycle_through_kept_action(template_stream):
    # an action that stops acting, followed by one that leads back to it. A
    # single /Next is written as an array, since pypdf 6.19 can't clone a
    # /Next dictionary whose own /Next is an array.
    def add(pdf, fields):
        reset = pdf.make_indirect(build_action(("reset", None), fields["test"]))
        first = pdf.make_indirect(
            Dictionary(S=Name.Named, N=Name.FirstPage, Next=Array([reset]))
        )
        reset.Next = Array([first, Dictionary(S=Name.Named, N=Name.LastPage)])
        get_button(pdf).AA = Dictionary(D=reset)

    expected, result = describe_removal(
        template_stream, add, lambda pdf: get_button(pdf).AA.D
    )

    assert expected == ["/Hide", "/FirstPage", "again", "/LastPage"]
    assert result == expected


@pytest.mark.parametrize("kept", [True, False])
def test_remove_fields_shared_action_branches(template_stream, kept):
    # each action that stops acting is followed twice by the next one, so
    # there are 4,096 paths to the last one. The first /Next is an array,
    # since pypdf 6.19 can't clone a /Next dictionary whose own /Next is an
    # array.
    def add(pdf, fields):
        action = pdf.make_indirect(build_action(("reset", None), fields["test"]))
        if kept:
            action.Next = pdf.make_indirect(Dictionary(S=Name.Named, N=Name.LastPage))
        for _ in range(12):
            parent = pdf.make_indirect(build_action(("reset", None), fields["test"]))
            parent.Next = Array([action, action])
            action = parent
        get_button(pdf).A = Dictionary(
            S=Name.JavaScript, JS=String("one"), Next=Array([action])
        )

    expected, result = describe_removal(
        template_stream, add, lambda pdf: get_button(pdf).A
    )

    assert result == expected


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ({"/AA": {"/U": "up"}}, (["/Hide"], ["/U"])),
        ({"/AA": {"/U": "reset"}}, ([], None)),
        ({"/AA": {"/D": "down"}}, ([], ["/D"])),
        ({"/Dest": True}, (["/Hide"], None)),
    ],
    ids=["mouse_up", "mouse_up_removed", "other_trigger", "destination"],
)
def test_remove_fields_keeps_overriding_action(template_stream, other, expected):
    # an annotation's /A takes precedence over its /AA /U, and a viewer may
    # read either /A or /Dest when both are present, so deleting /A would let
    # the other one act
    def add(pdf, fields):
        button = get_button(pdf)
        button.A = build_action(("reset", None), fields["test"])
        if "/Dest" in other:
            button.Dest = Array([pdf.pages[0].obj, Name.Fit])
        else:
            button.AA = Dictionary(
                {
                    trigger: build_action((label, None), fields["test"])
                    for trigger, label in other["/AA"].items()
                }
            )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        button = get_button(pdf)
        assert (
            describe_actions(button.get("/A")),
            sorted(str(trigger) for trigger in button.AA) if "/AA" in button else None,
        ) == expected


def test_remove_fields_keeps_repeated_actions(template_stream):
    # PDFium stops running a trigger's actions when it reaches one a second
    # time, so "k" never runs, before or after removal
    def add(pdf, fields):
        reset = pdf.make_indirect(build_action(("reset", None), fields["test"]))
        get_button(pdf).A = Dictionary(
            S=Name.JavaScript,
            JS=String("j"),
            Next=Array([reset, reset, Dictionary(S=Name.JavaScript, JS=String("k"))]),
        )

    expected, result = describe_removal(
        template_stream, add, lambda pdf: get_button(pdf).A
    )

    assert expected == ["j", "/Hide", "again", "k"]
    assert result == expected


@pytest.mark.parametrize("separately", [False, True])
def test_remove_fields_actions_in_separate_calls(template_stream, separately):
    # removing two fields in two calls leaves the same actions as in one
    def add(pdf, fields):
        second = pdf.make_indirect(
            Dictionary(S=Name.ResetForm, Fields=Array([fields["check"]]))
        )
        pdf.Root.OpenAction = Dictionary(
            S=Name.ResetForm, Fields=Array([fields["test"]]), Next=Array([second])
        )

    obj = PdfWrapper(with_actions(template_stream, add))
    if separately:
        with Pdf.open(BytesIO(obj.remove_fields(["test"]).read())) as pdf:
            assert describe_actions(pdf.Root.OpenAction) == ["/Hide", "/ResetForm"]
        obj.remove_fields(["check"])
    else:
        obj.remove_fields(["test", "check"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        assert "/OpenAction" not in pdf.Root


@pytest.mark.parametrize("separately", [False, True])
def test_remove_fields_overriding_action_in_separate_calls(template_stream, separately):
    # an /A kept only for the /AA /U it takes precedence over goes with it
    def add(pdf, fields):
        button = get_button(pdf)
        button.A = build_action(("reset", None), fields["test"])
        button.AA = Dictionary(
            U=Dictionary(S=Name.ResetForm, Fields=Array([fields["check"]]))
        )

    obj = PdfWrapper(with_actions(template_stream, add))
    if separately:
        with Pdf.open(BytesIO(obj.remove_fields(["test"]).read())) as pdf:
            button = get_button(pdf)
            assert describe_actions(button.A) == ["/Hide"]
            assert describe_actions(button.AA.U) == ["/ResetForm"]
        obj.remove_fields(["check"])
    else:
        obj.remove_fields(["test", "check"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        button = get_button(pdf)
        assert "/A" not in button
        assert "/AA" not in button


def test_remove_fields_long_action_chain(template_stream):
    # more actions that stop acting in one chain than Python's recursion
    # limit. The last action is indirect too, since pypdf 6.19 can't clone an
    # indirect action whose /Next is a direct one.
    def add(pdf, fields):
        action = pdf.make_indirect(Dictionary(S=Name.JavaScript, JS=String("after")))
        for _ in range(1050):
            reset = pdf.make_indirect(build_action(("reset", None), fields["test"]))
            reset.Next = action
            action = reset
        get_button(pdf).A = action

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        assert describe_actions(get_button(pdf).A) == ["/Hide"] * 1050 + ["after"]


@pytest.mark.parametrize("kind", ["indirect", "array"])
def test_remove_fields_resolves_action_types(template_stream, kind):
    # an indirect /S is resolved, and an /S that isn't a name, as in this
    # structure attribute, is not an action type
    def add(pdf, fields):
        if kind == "indirect":
            get_button(pdf).A = Dictionary(
                S=pdf.make_indirect(Name.ResetForm), Fields=Array([fields["test"]])
            )
        else:
            pdf.Root.StructTreeRoot = Dictionary(
                Type=Name.StructTreeRoot,
                K=Dictionary(
                    Type=Name.StructElem,
                    S=Name.P,
                    A=Dictionary(O=Name.Layout, S=Array([Name.ResetForm])),
                ),
            )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(["test"])

    with Pdf.open(BytesIO(obj.read())) as pdf:
        if kind == "indirect":
            assert "/A" not in get_button(pdf)
        else:
            attribute = pdf.Root.StructTreeRoot.K.A
            assert [str(each) for each in attribute.S] == ["/ResetForm"]


def test_remove_fields_widget_with_indirect_subtype(
    template_stream, assert_catalog_fields
):
    # PdfWrapper reads a widget whose /Subtype is an indirect /Widget, and
    # removing its field removes it from the page too
    with Pdf.open(BytesIO(template_stream)) as pdf:
        for annot in pdf.pages[1].Annots:
            if annot.get("/T") == "test_2":
                annot.Subtype = pdf.make_indirect(Name.Widget)
        stream = save(pdf)

    result = PdfWrapper(stream).remove_fields(["test_2"]).read()

    assert_catalog_fields(result, ["test", "check", "check_2", "test_3", "check_3"])


def test_remove_fields_hide_widget_not_in_catalog(template_stream):
    # a Hide action naming a page widget whose field isn't in /Fields
    def add(pdf, fields):
        pdf.Root.AcroForm.Fields = Array(
            [field for field in pdf.Root.AcroForm.Fields if field.T != "submit_button"]
        )
        fields["test"].A = Dictionary(
            S=Name.Hide, T=Array([String("submit_button"), String("check")])
        )

    obj = PdfWrapper(with_actions(template_stream, add)).remove_fields(
        ["submit_button"]
    )

    with Pdf.open(BytesIO(obj.read())) as pdf:
        test = next(annot for annot in pdf.pages[0].Annots if annot.get("/T") == "test")
        assert describe_targets(test.A.T) == ["check"]
