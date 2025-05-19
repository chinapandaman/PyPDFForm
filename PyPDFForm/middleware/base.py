# -*- coding: utf-8 -*-
"""Provides base widget middleware for PDF form elements.

This module contains the Widget base class that defines common functionality
and properties for all PDF form widgets, including:
- Name and value management
- Styling properties (borders, colors)
- Schema generation
- Basic validation
"""

from typing import Any


class Widget:
    """Abstract base class for all PDF form widget middleware.

    Provides common interface and functionality for:
    - Managing widget names and values
    - Handling visual properties (borders, colors)
    - Generating JSON schema definitions
    - Providing sample values

    Subclasses must implement:
    - sample_value property
    - Any widget-specific functionality
    """

    SET_ATTR_TRIGGER_HOOK_MAP = {}

    def __init__(
        self,
        name: str,
        value: Any = None,
    ) -> None:
        """Initializes a new widget with basic properties.

        Args:
            name: Field name/key for the widget
            value: Initial value for the widget (default: None)
        """

        super().__init__()
        self._name = name
        self._value = value
        self.desc = None
        self.border_color = None
        self.background_color = None
        self.border_width = None
        self.border_style = None
        self.dash_array = None
        self.render_widget = None
        self.hooks_to_trigger = []

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets an attribute on the widget with special handling for hook-triggering attributes.

        For attributes listed in SET_ATTR_TRIGGER_HOOK_MAP, when set to non-None values,
        adds a hook to hooks_to_trigger list with the mapped hook name and value.
        All other attributes are set normally via the standard object.__setattr__.

        Args:
            name: Name of the attribute to set
            value: Value to set the attribute to

        Note:
            The hook triggering only occurs when:
            1. The attribute is in SET_ATTR_TRIGGER_HOOK_MAP
            2. The value being set is not None
        """

        if name in self.SET_ATTR_TRIGGER_HOOK_MAP and value is not None:
            self.hooks_to_trigger.append((self.SET_ATTR_TRIGGER_HOOK_MAP[name], value))
        super().__setattr__(name, value)

    @property
    def name(self) -> str:
        """Gets the widget's field name/key.

        Returns:
            str: The widget's name as it appears in the PDF form
        """

        return self._name

    @property
    def value(self) -> Any:
        """Gets the widget's current value.

        Returns:
            Any: The widget's current value (type depends on widget type)
        """

        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        """Sets the widget's value.

        Args:
            value: New value for the widget (type depends on widget type)
        """

        self._value = value

    @property
    def schema_definition(self) -> dict:
        """Generates a JSON schema definition for the widget.

        Returns:
            dict: Schema properties including:
                - description (if available)
                - type constraints
                - other widget-specific properties
        """

        result = {}

        if self.desc is not None:
            result["description"] = self.desc

        return result

    @property
    def sample_value(self) -> Any:
        """Generates a sample value appropriate for the widget type.

        Returns:
            Any: A representative value demonstrating the widget's expected input

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError
