# -*- coding: utf-8 -*-

import os
from unittest.mock import patch

import pytest

from PyPDFForm import PdfWrapper
from tests.support.builders import without_default_appearance


@pytest.mark.parametrize(
    "template",
    [
        "sample_template.pdf",
        "sample_template_sejda.pdf",
        "sample_template_with_radio_button.pdf",
        os.path.join("dropdown", "sample_template_with_dropdown.pdf"),
    ],
)
def test_fill_readonly_updates_widgets(
    pdf_samples, template, assert_widgets_match_output
):
    obj = PdfWrapper(os.path.join(pdf_samples, template))
    obj.fill(obj.sample_data, readonly=True)

    assert all(widget.readonly is True for widget in obj.widgets.values())
    assert not any(widget.hooks_to_trigger for widget in obj.widgets.values())
    assert_widgets_match_output(obj)


def test_operations_keep_widgets_matching_output(
    template_stream, data_dict, assert_widgets_match_output
):
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].x = 200
    obj.widgets["check"].readonly = True
    assert_widgets_match_output(obj)

    obj.fill(data_dict)
    assert_widgets_match_output(obj)

    obj.remove_fields(["test_2", "check_2"])
    assert_widgets_match_output(obj)

    other = PdfWrapper(template_stream).fill(data_dict, readonly=True)
    merged = obj + other
    for each in (merged, obj, other):
        assert_widgets_match_output(each)


def test_commit_widget_key_updates_does_not_replay_hooks(
    template_stream, assert_widgets_match_output
):
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].tooltip = "tooltip"
    obj.widgets["test"].font_size = 20
    obj.read()
    obj.widgets["test"].readonly = False
    obj.fill({"test": "test"}, readonly=True)

    obj.update_widget_key("test", "renamed")
    obj.commit_widget_key_updates()
    stream = obj.read()

    renamed = obj.widgets["renamed"]
    # the earlier readonly=False is not applied again over the fill
    assert renamed.readonly is True
    assert not renamed.hooks_to_trigger
    # properties the PDF doesn't store are kept from the old widget
    assert renamed.font_size == 20
    assert obj.read() == stream
    assert_widgets_match_output(obj)


def test_commit_widget_key_updates_keeps_pending_value(
    template_stream, assert_round_trip
):
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].tooltip = "tooltip"
    obj.read()
    # assigned without filling, so only the wrapper has it
    obj.widgets["test"].value = "pending text"

    obj.update_widget_key("test", "renamed").commit_widget_key_updates()
    assert not obj.widgets["renamed"].hooks_to_trigger

    obj.fill({})
    assert_round_trip(obj, {"renamed": "pending text"})


def test_failed_hook_reverts_queued_updates(
    template_stream, assert_widgets_match_output
):
    obj = PdfWrapper(without_default_appearance(template_stream, "test"))
    original = obj.read()
    x = obj.widgets["test_2"].x
    obj.widgets["test_2"].x = 300
    obj.widgets["test"].font_size = 20

    # the font size can't be set without a default appearance
    with pytest.raises(ValueError, match="Cannot change /DA"):
        obj.read()

    assert obj.widgets["test_2"].x == x
    assert obj.widgets["test"].font_size is None
    assert not any(widget.hooks_to_trigger for widget in obj.widgets.values())
    # later reads don't retry the failed updates
    assert obj.read() == original
    assert obj.read() == original
    assert_widgets_match_output(obj)

    obj.widgets["test_2"].x = 300
    assert PdfWrapper(obj.read()).widgets["test_2"].x == 300


@pytest.mark.parametrize(
    ("choices", "index"), [(["bar"], 0), (["x", "y"], None)], ids=["moved", "cleared"]
)
def test_failed_hook_reverts_dropdown_selection(
    sample_template_with_dropdown, choices, index, assert_widgets_match_output
):
    obj = PdfWrapper(sample_template_with_dropdown).fill({"dropdown_1": 1})
    original = obj.read()
    widget = obj.widgets["dropdown_1"]
    widget.choices = choices
    assert widget.value == index

    with (
        patch("PyPDFForm.lib.wrapper.trigger_widget_hooks", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        obj.read()

    # the selection is restored with the choices
    assert widget.choices == ("foo", "bar", "foobar", " ")
    assert widget.value == 1
    assert obj.read() == original
    assert_widgets_match_output(obj)


def test_new_choices_keep_assigned_none(sample_template_with_dropdown):
    obj = PdfWrapper(sample_template_with_dropdown).fill({"dropdown_1": 1})
    obj.widgets["dropdown_1"].value = None
    obj.widgets["dropdown_1"].choices = ["bar", "foo"]
    output = obj.read()

    # assigning without filling changes only the wrapper, and reading doesn't
    # replace it with the PDF's selection
    assert obj.data["dropdown_1"] is None
    assert PdfWrapper(output).data["dropdown_1"] == 0


def test_new_choices_after_changing_list_in_place(sample_template_with_dropdown):
    obj = PdfWrapper(sample_template_with_dropdown)
    widget = obj.widgets["dropdown_1"]
    choices = ["a", "b", "c"]
    widget.choices = choices
    obj.fill({"dropdown_1": 2}).read()

    # the selected choice is removed from the wrapper's list, so its index has
    # no option to follow and is kept
    choices.pop()
    widget.choices = ["x"]
    assert widget.choices == ["x"]
    assert widget.value == 2
    hooks = list(widget.hooks_to_trigger)

    # choices that can't be read raise before the widget changes
    with pytest.raises(ValueError, match="too many values to unpack"):
        widget.choices = [("a", "b", "c")]
    assert widget.choices == ["x"]
    assert widget.value == 2
    assert widget.hooks_to_trigger == hooks


@pytest.mark.parametrize(
    "operation",
    [
        lambda obj: obj.remove_fields(["test_2"]),
        lambda obj: obj.commit_widget_key_updates(),
    ],
    ids=["remove_fields", "commit_widget_key_updates"],
)
def test_failed_operation_restores_wrapper(
    template_stream, operation, assert_widgets_match_output
):
    obj = PdfWrapper(template_stream)
    obj.widgets["test"].x = 200
    obj.update_widget_key("test", "renamed")
    original = obj.read()
    widgets = dict(obj.widgets)

    with (
        patch("PyPDFForm.lib.wrapper.build_widgets", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        operation(obj)

    assert obj.widgets == widgets
    assert obj.read() == original
    assert_widgets_match_output(obj)

    # the queued rename is kept, so it can still be committed
    obj.commit_widget_key_updates()
    assert "renamed" in obj.widgets
    assert "test" not in obj.widgets
    assert_widgets_match_output(obj)
