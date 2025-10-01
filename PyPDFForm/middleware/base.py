# -*- coding: utf-8 -*-
"""
Module containing base classes for middleware.

This module defines the base class for form widgets, which are used to
represent form fields in a PDF document. The Widget class provides
common attributes and methods for all form widgets, such as name, value,
and schema definition.
"""

from typing import Any


class Widget:
    """
    Base class for form widget.

    The Widget class provides a base implementation for form widgets,
    which are used to represent form fields in a PDF document. It
    defines common attributes and methods for all form widgets, such
    as name, value, and schema definition.
    """

    SET_ATTR_TRIGGER_HOOK_MAP = {
        "readonly": "flatten_generic",
        "required": "update_field_required",
        "tooltip": "update_field_tooltip",
    }

    def __init__(
        self,
        name: str,
        value: Any = None,
    ) -> None:
        """
        Initialize a new widget.

        Args:
            name (str): The name of the widget.
            value (Any): The initial value of the widget. Defaults to None.
        """
        super().__init__()
        self._name = name
        self._value = value
        self.tooltip: str = None
        self.readonly: bool = None
        self.required: bool = None
        self.hooks_to_trigger: list = []

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set an attribute on the widget.

        This method overrides the default __setattr__ method to
        trigger hooks when certain attributes are set.

        Args:
            name (str): The name of the attribute.
            value (Any): The value of the attribute.
        """
        if name in self.SET_ATTR_TRIGGER_HOOK_MAP and value is not None:
            self.hooks_to_trigger.append((self.SET_ATTR_TRIGGER_HOOK_MAP[name], value))
        super().__setattr__(name, value)

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
        self._value = value

    @property
    def schema_definition(self) -> dict:
        """
        Get the schema definition of the widget.

        This method returns a dictionary that defines the schema
        for the widget. The schema definition is used to validate
        the widget's value.

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
