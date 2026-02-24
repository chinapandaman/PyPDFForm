# -*- coding: utf-8 -*-
"""
Compares and diffs a single widget from two separate PDF files.

This script serializes a specified widget from two PDF files into a
human-readable string format. It then generates an HTML file that
highlights the differences between the two widget structures. The depth
of the serialization can be controlled.

The resulting diff is saved to temp/diff.html.

Usage:
    python scripts/diff_widget.py <file1.pdf> <file2.pdf> <widget_key> <recursion_depth>
"""

import sys
from difflib import HtmlDiff
from io import StringIO
from pprint import pprint

from pypdf.generic import ArrayObject, DictionaryObject

from PyPDFForm.patterns import get_widget_key
from PyPDFForm.template import get_widgets_by_page


def serializing_widget(widget, level):
    if hasattr(widget, "get_object"):
        widget = widget.get_object()

    level += 1
    if level == int(sys.argv[4]):
        return widget

    if isinstance(widget, (DictionaryObject, dict)):
        for k, v in widget.items():
            widget[k] = serializing_widget(v, level)
    elif isinstance(widget, ArrayObject):
        widget = ArrayObject([serializing_widget(each, level) for each in widget])

    return widget


def serializing_widget_from_file(filename, key, buff):
    with open(filename, "rb+") as f:
        widgets = get_widgets_by_page(f.read())

        for w in widgets.values():
            for widget in w:
                if get_widget_key(widget, False) == key:
                    pprint(serializing_widget(widget, 0), stream=buff)
                    buff.writelines("\n" * 3 + "=" * 100 + "\n" * 3)


if __name__ == "__main__":
    f1 = StringIO()
    f2 = StringIO()

    serializing_widget_from_file(sys.argv[1], sys.argv[3], f1)
    serializing_widget_from_file(sys.argv[2], sys.argv[3], f2)

    f1.seek(0)
    f2.seek(0)

    diff = HtmlDiff().make_file(f1.readlines(), f2.readlines())

    with open("temp/diff.html", "w") as f:
        f.write(diff)
