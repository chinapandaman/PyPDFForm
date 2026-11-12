# -*- coding: utf-8 -*-
"""
Module representing a checkbox widget.

This module defines the Checkbox class, which is a subclass of the
Widget class. It represents a checkbox form field in a PDF document.
"""

from typing import Any, Optional

from .base import Widget


class Checkbox(Widget):
    """
    Represents a checkbox widget.

    The Checkbox class provides a concrete implementation for
    checkbox form fields. It inherits from the Widget class and
    implements the schema_definition and sample_value properties.
    """

    TYPE_SPECIFIC_PROPERTIES = frozenset({"size"})
    GEOMETRY_PROPERTIES = Widget.GEOMETRY_PROPERTIES | {"size"}

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
        super().__init__(name, value)
        self.SET_ATTR_TRIGGER_HOOK_MAP.update(
            {
                "size": "update_check_radio_size",
            }
        )

        self.size: Optional[float] = None

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Custom attribute setter for the Checkbox class.

        The parent class's setter validates the attribute and queues its hook.
        When 'size' is set after construction, both 'width' and 'height' are then
        set to the same value, ensuring the checkbox remains square and all
        relevant hooks are queued.

        Args:
            name (str): The name of the attribute to set.
            value (Any): The value to set for the attribute.

        Raises:
            TypeError: Raised when the size is None or not a number.
        """
        constructed = name in self.__dict__
        super().__setattr__(name, value)
        if name == "size" and constructed:
            super().__setattr__("width", value)
            super().__setattr__("height", value)

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
    def sample_value(self) -> bool | int | None:
        """
        Returns a sample value for the checkbox.

        The sample value is used to generate example data for the
        checkbox field.

        Returns:
            bool | int | None: A sample value for the checkbox or its subclasses.
        """
        return True
