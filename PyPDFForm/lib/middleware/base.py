# -*- coding: utf-8 -*-
"""
Module containing base classes for middleware.

This module defines the base class for form widgets, which are used to
represent form fields in a PDF document. The Widget class provides
common attributes and methods for all form widgets, such as name, value,
and schema definition.
"""

from dataclasses import dataclass
from typing import Any, List, Optional, TextIO


@dataclass(frozen=True)
class PreparedValue:
    """
    Represents a widget value prepared for assignment.

    Preparation validates and normalizes the value without changing the widget.
    Dropdown updates can also include replacement choices, which are stored and
    queued for PDF updates only when the prepared value is applied.

    Attributes:
        value (Any): The value to store in the widget.
        choices (list | None): Replacement dropdown choices, or None when the
            choices should remain unchanged.
    """

    value: Any
    choices: list | None = None


class Widget:
    """
    Base class for form widget.

    The Widget class provides a base implementation for middleware objects
    built from existing PDF form fields. It stores extracted field state,
    queues hook calls when mutable attributes are changed, and exposes schema
    and sample-data helpers used by `PdfWrapper`.

    Attributes:
        TYPE_SPECIFIC_PROPERTIES (frozenset): Properties supported only by this
            widget type and its subclasses. Subclasses declare their own.
    """

    TYPE_SPECIFIC_PROPERTIES = frozenset()
    _ALL_TYPE_SPECIFIC_PROPERTIES = set()

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Registers the type-specific properties declared by a subclass.

        The registry holds the properties declared by every widget type, so a
        widget can reject properties that only other widget types support.

        Args:
            **kwargs: Keyword arguments passed to the parent hook.
        """
        super().__init_subclass__(**kwargs)
        Widget._ALL_TYPE_SPECIFIC_PROPERTIES.update(cls.TYPE_SPECIFIC_PROPERTIES)

    def __init__(
        self,
        name: str,
        value: Any = None,
    ) -> None:
        """
        Initialize a new widget.

        The constructor initializes common metadata, geometry, JavaScript hook
        attributes, and the map from public attribute names to hook functions.

        Args:
            name (str): The name of the widget.
            value (Any): The initial value of the widget. Defaults to None.
        """
        super().__init__()
        self.SET_ATTR_TRIGGER_HOOK_MAP = {
            "x": "update_field_x",
            "y": "update_field_y",
            "width": "update_field_width",
            "height": "update_field_height",
            "readonly": "update_field_readonly",
            "required": "update_field_required",
            "hidden": "update_field_hidden",
            "tooltip": "update_field_tooltip",
            "on_hovered_over_javascript": "update_field_on_hovered_over_javascript",
            "on_hovered_off_javascript": "update_field_on_hovered_off_javascript",
            "on_mouse_pressed_javascript": "update_field_on_mouse_pressed_javascript",
            "on_mouse_released_javascript": "update_field_on_mouse_released_javascript",
            "on_focused_javascript": "update_field_on_focused_javascript",
            "on_blurred_javascript": "update_field_on_blurred_javascript",
        }
        self.attr_set_tracker = {}

        self._name = name
        self._value = value

        self.tooltip: Optional[str] = None
        self.readonly: Optional[bool] = None
        self.required: Optional[bool] = None
        self.hidden: Optional[bool] = None
        self.hooks_to_trigger: list = []

        # coordinate & dimension
        self.page_number: Optional[int] = None
        self.x: Optional[float | List[float]] = None
        self.y: Optional[float | List[float]] = None
        self.width: Optional[float | List[float]] = None
        self.height: Optional[float | List[float]] = None

        # javascript
        self.on_hovered_over_javascript: Optional[str | TextIO] = None
        self.on_hovered_off_javascript: Optional[str | TextIO] = None
        self.on_mouse_pressed_javascript: Optional[str | TextIO] = None
        self.on_mouse_released_javascript: Optional[str | TextIO] = None
        self.on_focused_javascript: Optional[str | TextIO] = None
        self.on_blurred_javascript: Optional[str | TextIO] = None

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set an attribute on the widget.

        This method overrides the default __setattr__ method to
        trigger hooks when certain attributes are set to non-None values. It also
        tracks existing attributes that were explicitly set so those values can be
        preserved across widget-cache rebuilds. Type-specific properties that the
        widget does not support are rejected before any change.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute.

        Raises:
            AttributeError: Raised when the widget type does not support the
                property.
        """
        self.check_property_supported(name)

        if (
            hasattr(self, "SET_ATTR_TRIGGER_HOOK_MAP")
            and name in self.SET_ATTR_TRIGGER_HOOK_MAP
            and value is not None
        ):
            self.hooks_to_trigger.append((self.SET_ATTR_TRIGGER_HOOK_MAP[name], value))

        if (
            hasattr(self, "attr_set_tracker")
            and name in self.__dict__
            and value is not None
        ):
            self.attr_set_tracker[name] = value

        super().__setattr__(name, value)

    def check_property_supported(self, name: str) -> None:
        """
        Checks whether the widget type supports a property.

        Type-specific properties, such as `max_length` or `size`, are supported
        only by widget types that declare them in `TYPE_SPECIFIC_PROPERTIES`.
        Other attribute names are not checked.

        Args:
            name (str): The name of the property.

        Raises:
            AttributeError: Raised when the widget type does not support the
                property.
        """
        if (
            name in Widget._ALL_TYPE_SPECIFIC_PROPERTIES
            and name not in self.TYPE_SPECIFIC_PROPERTIES
        ):
            msg = (
                f"{type(self).__name__} field '{self.name}' does not support "
                f"property '{name}'."
            )
            raise AttributeError(msg)

    @property
    def name(self) -> str:
        """
        Get the name of the widget.

        Returns:
            str: The name of the widget.
        """
        return self._name

    @property
    def value(self) -> Any:
        """
        Get the value of the widget.

        Returns:
            Any: The value of the widget.
        """
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """
        Set the value of the widget.

        Args:
            value (Any): The value to set.
        """
        self.apply_value(self.prepare_value(value))

    def prepare_value(self, value: Any) -> PreparedValue:
        """
        Prepares a value for assignment without changing the widget.

        The base implementation retains the supplied value. Subclasses can
        validate or normalize it and stage related attribute changes here.

        Args:
            value (Any): The proposed value of the widget.

        Returns:
            PreparedValue: The value to apply after preparation succeeds.
        """
        return PreparedValue(value)

    def apply_value(self, update: PreparedValue) -> None:
        """
        Applies a previously prepared value to the widget.

        This method stores the value without repeating validation. Subclasses
        can apply related attribute changes through their existing hooks.

        Args:
            update (PreparedValue): The prepared widget value to store.
        """
        self._value = update.value

    @property
    def schema_definition(self) -> dict:
        """
        Get the schema definition of the widget.

        This method returns the common schema fragment for the widget. Subclasses
        merge their type-specific schema into this fragment. The base fragment
        currently contributes the tooltip as a JSON Schema description when one
        is available.

        Returns:
            dict: The schema definition of the widget.
        """
        result = {}

        if self.tooltip is not None:
            result["description"] = self.tooltip

        return result

    @property
    def sample_value(self) -> Any:
        """
        Get a sample value for the widget.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError
