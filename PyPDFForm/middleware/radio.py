# -*- coding: utf-8 -*-
"""Provides middleware for PDF radio button widgets.

This module contains the Radio class which handles:
- Radio button group state management
- Option selection tracking
- Value validation and conversion
- Schema generation for form validation
"""

from .checkbox import Checkbox


class Radio(Checkbox):
    """Middleware for PDF radio button widgets.

    Handles all aspects of radio button processing including:
    - Group selection management
    - Option counting and validation
    - Button style customization
    - PDF form field integration

    Inherits from Checkbox class and extends it with radio-specific features.
    """

    def __init__(
        self,
        name: str,
        value: int = None,
    ) -> None:
        """Initializes a new radio button widget.

        Args:
            name: Field name/key for the radio button group
            value: Initial selected option index (default: None)
        """

        super().__init__(name, value)

        self.size = None
        self.number_of_options = 0
        self._button_style = self.BUTTON_STYLE_MAPPING["circle"]

    @property
    def schema_definition(self) -> dict:
        """Generates a JSON schema definition for the radio button group.

        Includes:
        - Type constraint (integer)
        - Maximum valid option index
        - Any inherited schema properties

        Returns:
            dict: Complete JSON schema definition
        """

        return {
            "maximum": self.number_of_options - 1,
            **super().schema_definition,
            "type": "integer",
        }

    @property
    def sample_value(self) -> int:
        """Generates a sample value for the radio button group.

        Returns the index of the last option by default.

        Returns:
            int: Index of the last option in the group
        """

        return self.number_of_options - 1
