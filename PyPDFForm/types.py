# -*- coding: utf-8 -*-
"""
A module for custom type definitions used throughout the PyPDFForm library.

This includes specialized container types like PdfWrapperList, which extends
the standard list to provide custom behavior for slicing operations, particularly
for merging PdfWrapper objects.
"""


class PdfWrapperList(list):
    """
    A specialized list subclass designed to hold PdfWrapper objects.

    When sliced, this list automatically merges the contained PdfWrapper
    objects using the PdfWrapper.__add__ method, returning a single
    merged PdfWrapper object. If the slice is empty, it returns an empty list.
    For non-slice indexing, it behaves like a standard list.
    """

    def __getitem__(self, key: any) -> list | any:
        """
        Retrieves an item or a slice of items from the list.

        If the key is a slice, it merges the PdfWrapper objects in the slice
        and returns a single merged PdfWrapper.
        If the key is an index, it returns the PdfWrapper at that index.

        Args:
            key (Union[int, slice]): The index or slice to retrieve.

        Returns:
            Union[PdfWrapper, list, any]: A single merged PdfWrapper if sliced,
                                          or the item at the index if indexed.
        """

        if isinstance(key, slice):
            result = None
            l = super().__getitem__(key)
            for each in l:
                if not result:
                    result = each
                else:
                    result += each

            return result if result else []
        else:
            return super().__getitem__(key)
