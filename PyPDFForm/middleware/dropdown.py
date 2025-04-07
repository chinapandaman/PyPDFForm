# -*- coding: utf-8 -*-
"""Provides middleware for PDF dropdown/combobox widgets.

This module contains the Dropdown class which handles:
- Dropdown option management
- Selection index tracking
- Value validation
- Schema generation for form validation
"""

from .base import Widget


class Dropdown(Widget):
    """Middleware for PDF dropdown/combobox widgets.

    Handles all aspects of dropdown processing including:
    - Option list management
    - Selection index validation
    - Value conversion
    - PDF form field integration

    Inherits from Widget base class and extends it with dropdown-specific features.
    """

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """Initializes a new dropdown widget.

        Args:
            name: Field name/key for the dropdown
            value: Initial selected option index (default: None)
        """

        super().__init__(name, value)

        self.choices = []
        self.desc = None

    @property
    def schema_definition(self) -> dict:
        """Generates a JSON schema definition for the dropdown.

        Includes:
        - Type constraint (integer)
        - Maximum valid option index
        - Any inherited schema properties

        Returns:
            dict: Complete JSON schema definition
        """

        return {
            "type": "integer",
            "maximum": len(self.choices) - 1,
            **super().schema_definition,
        }

    @property
    def sample_value(self) -> int:
        """Generates a sample value for the dropdown.

        Returns the index of the last option by default.

        Returns:
            int: Index of the last option in the dropdown
        """

        return len(self.choices) - 1
