# -*- coding: utf-8 -*-
"""
Module representing a checkbox widget.

This module defines the Checkbox class, which is a subclass of the
Widget class. It represents a checkbox form field in a PDF document.
"""

from typing import Union

from .base import Widget


class Checkbox(Widget):
    """
    Represents a checkbox widget.

    The Checkbox class provides a concrete implementation for
    checkbox form fields. It inherits from the Widget class and
    implements the schema_definition and sample_value properties.
    """

    def __init__(
        self,
        name: str,
        value: bool = None,
    ) -> None:
        """
        Initializes a checkbox widget.

        Args:
            name (str): The name of the checkbox.
            value (bool): The initial value of the checkbox. Defaults to None.

        Attributes:
            size (int): The size of the checkbox. Defaults to None.
        """
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "size": "update_check_radio_size",
            }
        )
        super().__init__(name, value)

        self.size: float = None

    @property
    def schema_definition(self) -> dict:
        """
        Returns the schema definition for the checkbox.

        The schema definition is a dictionary that describes the
        data type and other constraints for the checkbox value.

        Returns:
            dict: A dictionary representing the schema definition.
        """
        return {"type": "boolean", **super().schema_definition}

    @property
    def sample_value(self) -> Union[bool, int]:
        """
        Returns a sample value for the checkbox.

        The sample value is used to generate example data for the
        checkbox field.

        Returns:
            Union[bool, int]: A sample value for the checkbox.
        """
        return True
