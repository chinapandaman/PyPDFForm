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
    and sample-data helpers used by `PdfWrapper`. Each queued property keeps
    its committed value so a failed update can be reverted.

    Attributes:
        TYPE_SPECIFIC_PROPERTIES (frozenset): Properties supported only by this
            widget type and its subclasses. Subclasses declare their own.
        READ_PROPERTIES (frozenset): Hooked properties read back from the PDF
            when a wrapper is opened. Other hooked properties, such as fonts and
            JavaScript, exist only on the widget.
        CLEARABLE_PROPERTIES (frozenset): Read properties that are absent from
            the PDF when None. Assigning None removes them from the PDF.
        GEOMETRY_PROPERTIES (frozenset): Coordinates and dimensions, which must
            be integers or floats. Subclasses add their own, such as `size`.
    """

    TYPE_SPECIFIC_PROPERTIES = frozenset()
    READ_PROPERTIES = frozenset(
        {"x", "y", "width", "height", "readonly", "required", "hidden", "tooltip"}
    )
    CLEARABLE_PROPERTIES = frozenset({"tooltip"})
    GEOMETRY_PROPERTIES = frozenset({"x", "y", "width", "height"})
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
        self._committed_values = {}

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

        This method overrides the default __setattr__ method. After the widget
        is constructed, assigning a hooked property validates the value with
        `prepare_property` and queues a hook that applies it to the PDF on the
        next read. The property's committed value is kept until the hook is
        applied or reverted. None queues a hook only for clearable properties.
        Type-specific properties that the widget does not support are rejected
        before any change.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute.

        Raises:
            AttributeError: Raised when the widget type does not support the
                property.
            TypeError: Raised when a property read back from the PDF is set to
                None, or geometry is not a number.
            ValueError: Raised when a value is outside its valid range.
        """
        self.check_property_supported(name)

        hook = self.__dict__.get("SET_ATTR_TRIGGER_HOOK_MAP", {}).get(name)
        if hook is not None and name in self.__dict__:
            value, hook_value = self.prepare_property(name, value)
            if hook_value is not None or name in self.CLEARABLE_PROPERTIES:
                self._committed_values.setdefault(name, self.__dict__[name])
                self.hooks_to_trigger.append((hook, hook_value))

        super().__setattr__(name, value)

    def prepare_property(self, name: str, value: Any) -> tuple[Any, Any]:
        """
        Validates a hooked property value before the widget changes.

        Properties read back from the PDF must be values the PDF can store, so
        reopening the PDF reports the same value. None is accepted only for
        clearable properties, and an empty tooltip clears the tooltip. Geometry
        must be an integer or float. Subclasses can validate their own
        properties and change how a value is stored.

        Args:
            name (str): The name of the property.
            value (Any): The proposed value of the property.

        Returns:
            tuple[Any, Any]: The value to store on the widget and the value to
                pass to the property's hook.

        Raises:
            TypeError: Raised when a property read back from the PDF is set to
                None, or geometry is not a number.
        """
        if value is None:
            if (
                name in self.READ_PROPERTIES or name in self.GEOMETRY_PROPERTIES
            ) and name not in self.CLEARABLE_PROPERTIES:
                msg = (
                    f"{type(self).__name__} field '{self.name}' property "
                    f"'{name}' cannot be None."
                )
                raise TypeError(msg)
        elif name in self.GEOMETRY_PROPERTIES:
            self.validate_geometry_value(value)
        elif name == "tooltip" and value == "":
            value = None

        return value, value

    @staticmethod
    def validate_geometry_value(value: Any) -> int | float:
        """
        Validates a scalar coordinate or dimension.

        Args:
            value (Any): The coordinate or dimension to validate.

        Returns:
            int | float: The unchanged value.

        Raises:
            TypeError: If the value is not an integer or float, or is a boolean.
        """
        # bool subclasses int, so the numeric type check alone would accept booleans.
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            # TODO: Refactor this raise into a centralized exception raiser when one is introduced.
            msg = "Geometry values must be integers or floats; booleans are invalid."
            raise TypeError(msg)
        return value

    def save_state(self) -> dict:
        """
        Returns a copy of the widget's attributes, queued hooks, and committed values.

        Returns:
            dict: The state to pass to `restore_state`.
        """
        return {
            **self.__dict__,
            "hooks_to_trigger": list(self.hooks_to_trigger),
            "_committed_values": dict(self._committed_values),
        }

    def restore_state(self, state: dict) -> None:
        """
        Restores attributes saved by `save_state` without queuing hooks.

        Args:
            state (dict): The state returned by `save_state`.
        """
        self.__dict__.clear()
        self.__dict__.update(state)

    def clear_property_updates(self) -> None:
        """
        Clears queued hooks and committed values after hooks are applied.
        """
        self.hooks_to_trigger = []
        self._committed_values = {}

    def revert_property_updates(self) -> None:
        """
        Discards queued hooks and restores their properties' committed values.

        Values are restored without queuing hooks, so the widget again matches
        the PDF the hooks were not applied to.
        """
        for name, value in self._committed_values.items():
            self.__dict__[name] = value
        self.clear_property_updates()

    def copy_unread_state(self, other: "Widget") -> None:
        """
        Copies the state that rebuilding a widget from the PDF would lose.

        A widget rebuilt from the PDF, such as after renaming, takes the value
        of the widget it replaces, since a value assigned without filling is not
        in the PDF yet. It also takes the hooked properties that are not read
        back from the PDF, such as fonts, sizes, and JavaScript. A value of None
        keeps the value read from the PDF. Nothing is copied through hooks, so
        no update is queued again.

        Args:
            other (Widget): The widget to copy the state from.
        """
        if other.__dict__.get("_value") is not None:
            self.__dict__["_value"] = other.__dict__["_value"]

        for name in self.SET_ATTR_TRIGGER_HOOK_MAP:
            if name not in self.READ_PROPERTIES and name in other.__dict__:
                self.__dict__[name] = other.__dict__[name]

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
