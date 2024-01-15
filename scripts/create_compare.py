# -*- coding: utf-8 -*-
"""Creates compare of PDFs between changes."""

import os
import sys

if __name__ == "__main__":
    path = sys.argv[1]

    with open(os.path.abspath(path), "rb+") as f:
        file_name = os.path.basename(os.path.abspath(path))

        with open(os.path.join(os.path.dirname(__file__), "..", "temp", file_name), "wb+") as o:
            o.write(f.read())
