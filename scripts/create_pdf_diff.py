# -*- coding: utf-8 -*-
"""
Saves a temporary copy of a PDF file for later comparison.

This script takes the file path of a PDF as a command-line argument and
creates a copy of it in the project's 'temp' directory. The copied
file is renamed by replacing path separators with underscores to create a
unique, flat filename. This is used to store a "before" state of a file
before it is modified, allowing a "diff" to be generated later.

Usage:
    python scripts/create_pdf_diff.py <path_to_pdf>
"""

import os
import sys

if __name__ == "__main__":
    path = sys.argv[1]

    with open(os.path.abspath(path), "rb+") as f:
        file_name = "_".join(path.split("/"))

        with open(
            os.path.join(os.path.dirname(__file__), "..", "temp", file_name), "wb+"
        ) as o:
            o.write(f.read())
