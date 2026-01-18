# -*- coding: utf-8 -*-
"""
A module for custom type definitions used throughout the PyPDFForm library.

This includes specialized container types like PdfArray, which extends
the standard list to provide custom behavior for slicing operations, particularly
for merging PdfWrapper objects.
"""

from typing import Any, Union

from .utils import generic_merge


class PdfArray(list):
    """
    A specialized list subclass designed to hold PdfWrapper objects.

    When sliced, this list automatically merges the contained PdfWrapper
    objects using the PdfWrapper.__add__ method, returning a single
    merged PdfWrapper object. If the slice is empty, it returns an empty list.
    For non-slice indexing, it behaves like a standard list.
    """

    def __getitem__(self, key: Any) -> Union[list, Any]:
        """
        Retrieves an item or a slice of items from the list.

        If the key is a slice, it merges the PdfWrapper objects in the slice
        and returns a single merged PdfWrapper.
        If the key is an index, it returns the PdfWrapper at that index.

        Args:
            key (Union[int, slice]): The index or slice to retrieve.

        Returns:
            Union[PdfWrapper, list, Any]: A single merged PdfWrapper if sliced,
                                          or the item at the index if indexed.
        """

        if isinstance(key, slice):
            result = None
            wrappers = super().__getitem__(key)
            for each in wrappers:
                if not result:
                    result = each
                else:
                    result += each

            return result
        return super().__getitem__(key)

    def merge(self) -> Any:
        """
        Merges all PdfWrapper objects in the list into a single PdfWrapper.

        This method uses a pairwise merging strategy to combine all PdfWrapper
        objects contained in the list into one.

        Returns:
            Any: A single merged PdfWrapper object.
        """
        return generic_merge(list(self), lambda x, y: x + y)
