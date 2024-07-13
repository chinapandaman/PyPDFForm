# -*- coding: utf-8 -*-
"""Bumps a minor version."""

import os
import re
import sys

if __name__ == "__main__":
    branch = sys.argv[1]
    if not branch.startswith("PPF-"):
        print("Bump version cannot be done on a non-issue branch.")
        sys.exit(1)

    v = ""
    with open("PyPDFForm/__init__.py", encoding="utf8") as f:
        version = re.search(r'__version__ = "(.*?)"', f.read())
        if version:
            v = version.group(1)

    new_version = ".".join(v.split(".")[:-1] + [str(int(v.split(".")[-1]) + 1)])

    files_to_update = ["PyPDFForm/__init__.py", "mkdocs.yml", "SECURITY.md"]

    for each in files_to_update:
        with open(each, encoding="utf8") as f:
            content = f.read().replace(v, new_version)

        os.remove(each)
        with open(each, mode="w", encoding="utf8") as f:
            f.write(content)
