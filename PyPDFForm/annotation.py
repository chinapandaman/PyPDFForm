# -*- coding: utf-8 -*-

from typing import Union


class Annotation(object):
    """A class to represent an annotation of a PDF form."""

    def __init__(
        self, annot_name: str, annot_type: str, annot_value: Union[str, bool] = None
    ) -> None:
        """Constructs all attributes for the Annotation object."""

        self.name = annot_name
        self.type = annot_type
        self.value = annot_value
