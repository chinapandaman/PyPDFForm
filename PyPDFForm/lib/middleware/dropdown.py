# -*- coding: utf-8 -*-
"""
Module representing a dropdown widget.

This module defines the Dropdown class, which is a subclass of the
Widget class. It represents a dropdown form field in a PDF document.
It also defines DropdownOption, the single representation used to convert
dropdown options between public choices and PDF option arrays.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Optional, Sequence

from pypdf.generic import ArrayObject, TextStringObject

from .base import PreparedValue, Widget


@dataclass(frozen=True)
class DropdownOption:
    """
    Represents one dropdown option with its displayed text and export value.

    Public choices use a string when both values are equal, or a
    `(display, export)` sequence when they differ. PDF option arrays store the
    same pair in the opposite order, `[export, display]`, and a field's `/V`
    holds the export value of the selected option.

    Attributes:
        display (str): The text shown for the option.
        export (str): The value stored in the PDF when the option is selected.
    """

    display: str
    export: str

    @classmethod
    def from_choice(cls, choice: str | Sequence[str]) -> DropdownOption:
        """
        Creates an option from a public choice.

        Args:
            choice (str | Sequence[str]): A string used as both the displayed
                text and export value, or a `(display, export)` sequence.

        Returns:
            DropdownOption: The option described by the choice.
        """
        if isinstance(choice, str):
            return cls(choice, choice)
        display, export = choice
        return cls(display, export)

    @classmethod
    def from_pdf(cls, entry: Any) -> DropdownOption:
        """
        Creates an option from an entry of a PDF `/Opt` array.

        Args:
            entry (Any): A text string used as both values, or an
                `[export, display]` array.

        Returns:
            DropdownOption: The option described by the entry.
        """
        entry = entry.get_object()
        if isinstance(entry, str):
            return cls(str(entry), str(entry))
        return cls(str(entry[1]), str(entry[0]))

    @property
    def choice(self) -> str | tuple[str, str]:
        """
        Returns the option in the public choices format.

        Returns:
            str | tuple[str, str]: The displayed text when it equals the export
                value, otherwise a `(display, export)` tuple.
        """
        if self.display == self.export:
            return self.display
        return self.display, self.export

    def to_pdf(self) -> ArrayObject:
        """
        Returns the option as an entry of a PDF `/Opt` array.

        Returns:
            ArrayObject: The `[export, display]` array for the option.
        """
        return ArrayObject(
            [TextStringObject(self.export), TextStringObject(self.display)]
        )


class Dropdown(Widget):
    """
    Represents a dropdown widget in a PDF form.

    Inherits from the Widget class and provides specific functionality
    for handling dropdown form fields. The stored value is an option index; string
    assignments select the option whose displayed text or export value matches,
    or are appended as a new choice when none does. Strings matching options that
    differ are rejected. Integer indices must identify an existing option.

    Key attributes:
        font (str): The font of the dropdown field.
        choices (List[str | Tuple[str, str]]): The available options. Each is a
            string when its displayed text and export value are equal, or a
            `(display, export)` tuple when they differ.
        value (int): The index of the selected choice in the choices list.

    Methods:
        schema_definition: Returns a schema definition for the dropdown's value.
        sample_value: Returns a sample value for the dropdown.
    """

    TYPE_SPECIFIC_PROPERTIES = frozenset({"font", "font_size", "font_color", "choices"})

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """
        Initializes a dropdown widget.

        Besides common widget state, dropdowns register hooks for font updates
        and choice replacement.

        Args:
            name (str): The name of the dropdown.
            value (int): The initial value of the dropdown. Defaults to None.

        Attributes:
            font (str): The font of the dropdown field.
            choices (List[str | Tuple[str, str]]): The list of choices for the
                dropdown, as strings or `(display, export)` tuples.
        """
        super().__init__(name, value)
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "font": "update_text_field_font",
                "choices": "update_dropdown_choices",
                "font_size": "update_text_field_font_size",
                "font_color": "update_text_field_font_color",
            }
        )

        self.font: Optional[str] = None
        self.font_size: Optional[float] = None
        self.font_color: Optional[tuple] = None
        self.choices: Optional[tuple | list] = None

    @property
    def value(self) -> int:
        """
        Gets the current value of the dropdown.

        Returns:
            int: The index of the selected choice.
        """
        return super().value

    @value.setter
    def value(self, value: str | int) -> None:
        """
        Sets the value of the dropdown.

        If the value is a string, it selects the option whose displayed text
        or export value matches it. If none matches, the string value is
        added to the choices, and its new index is used. Integer values are checked
        against the current choices before being stored.

        Args:
            value (str | int): The value to set. Can be a string
                (displayed text or export value) or an integer (index).

        Raises:
            ValueError: If an integer index is outside the current choices, or
                a string matches options that differ.
        """
        self.apply_value(self.prepare_value(value))

    @property
    def options(self) -> tuple[DropdownOption, ...]:
        """
        Returns the current choices as options with explicit export values.

        Returns:
            tuple[DropdownOption, ...]: The options, in choice order.
        """
        return tuple(DropdownOption.from_choice(each) for each in self.choices or ())

    def prepare_value(self, value: Any) -> PreparedValue:
        """
        Prepares a dropdown selection without changing its value or choices.

        Integer indices are checked against the current choices. Strings are
        normalized to the index of the option whose displayed text or export
        value matches, or staged as a new last option, keeping the existing
        choices and their export values. New choices do not trigger hooks until
        the prepared selection is applied.

        Args:
            value (Any): The proposed displayed text, export value, or index.

        Returns:
            PreparedValue: The selected index and any replacement choices.

        Raises:
            ValueError: If an integer index is outside the current choices, or
                a string matches options that differ.
        """
        self.validate_choice_index(value)
        if isinstance(value, str):
            index = self._get_option_index(value)
            if index is None:
                choices = list(self.choices or ()) + [value]
                return PreparedValue(len(choices) - 1, choices)
            value = index

        return super().prepare_value(value)

    def apply_value(self, update: PreparedValue) -> None:
        """
        Applies a previously prepared dropdown selection.

        Replacement choices are stored through the existing attribute setter
        so their PDF update hook is queued before the selected index is stored.
        Validation and option lookup are not repeated during application.

        Args:
            update (PreparedValue): The prepared selection and optional choices.
        """
        if update.choices is not None:
            self.choices = update.choices
        super().apply_value(update)

    def choice_index_schema(self) -> dict:
        """
        Returns the schema definition for indices into the current choices.

        Valid indices range from zero to the number of choices minus one. An
        empty dropdown explicitly rejects every integer selection.

        Returns:
            dict: A dictionary representing the schema definition for indices.
        """
        number_of_options = len(self.choices or [])
        if not number_of_options:
            return {"type": "integer", "not": {}}
        return {"type": "integer", "minimum": 0, "maximum": number_of_options - 1}

    def validate_choice_index(self, value: object) -> None:
        """
        Validates an integer selection against the current dropdown choices.

        Non-integer values retain their existing handling, including strings
        normalized during preparation and None for an unset selection.

        Args:
            value (object): The proposed value of the dropdown.

        Raises:
            ValueError: If an integer index is outside the current choices.
        """
        number_of_options = len(self.choices or [])
        if isinstance(value, int) and not 0 <= value < number_of_options:
            msg = f"Choice index {value} must satisfy 0 <= index < {number_of_options}."
            raise ValueError(msg)

    def _get_option_index(self, value: str) -> int | None:
        """
        Gets the index of the option whose displayed text or export value matches.

        Identical options, with the same displayed text and export value, are
        interchangeable, so the first is used.

        Args:
            value (str): The displayed text or export value to search for.

        Returns:
            int | None: The index of the option if found, otherwise None.

        Raises:
            ValueError: If the value matches options that differ.
        """
        options = self.options
        matches = [
            i for i, each in enumerate(options) if value in (each.display, each.export)
        ]
        if len({options[i] for i in matches}) > 1:
            msg = (
                f"Dropdown value {value!r} matches the options at indices {matches}; "
                "use an option index instead."
            )
            raise ValueError(msg)

        return matches[0] if matches else None

    def get_selected_index(self, value: Any, indices: Any) -> int | None:
        """
        Gets the index of the option selected by a PDF field value.

        Export values are matched first, because a field's `/V` holds the export
        value. Displayed text is matched only when no export value matches, so
        fields filled with displayed text are still read. Among matching options,
        the first index in `/I`, which can be an indirect object, is used when it
        is one of them; otherwise the first match is used.

        Args:
            value (Any): The field's `/V` entry.
            indices (Any): The field's `/I` entry.

        Returns:
            int | None: The index of the selected option, or None when no option
                matches.
        """
        options = self.options
        # array elements are not resolved by subscripting
        hint = (
            indices[0].get_object() if isinstance(indices, list) and indices else None
        )
        for matches in (
            [i for i, each in enumerate(options) if each.export == value],
            [i for i, each in enumerate(options) if each.display == value],
        ):
            if matches:
                return hint if hint in matches else matches[0]

        return None

    def ambiguous_values(self) -> list[str]:
        """
        Returns the strings that match options that differ.

        Returns:
            list[str]: The sorted displayed texts and export values that a string
                selection rejects.
        """
        matches = defaultdict(set)
        for each in self.options:
            matches[each.display].add(each)
            matches[each.export].add(each)

        return sorted(value for value, options in matches.items() if len(options) > 1)

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the dropdown.

        The schema definition accepts either an integer option index bounded by
        the current choices or a string value that can be normalized by the value
        setter. Strings that match options that differ are excluded.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        string_schema: dict = {"type": "string"}
        ambiguous = self.ambiguous_values()
        if ambiguous:
            string_schema["not"] = {"enum": ambiguous}

        return {
            "anyOf": [
                {
                    **self.choice_index_schema(),
                    **super().schema_definition,
                },
                string_schema,
            ]
        }

    @property
    def sample_value(self) -> int | None:
        """
        Returns a sample value for the dropdown.

        The sample value is used to generate example data for the
        dropdown field. It selects the last available option, or returns None
        when no choices are available so sample data can omit the field.

        Returns:
            int | None: The last option index, or None when there are no choices.
        """
        return len(self.choices) - 1 if self.choices else None
