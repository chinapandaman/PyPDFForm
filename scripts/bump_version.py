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

    to_bump = sys.argv[2]

    v = ""
    with open("PyPDFForm/__init__.py", encoding="utf8") as f:
        version = re.search(r'__version__ = "(.*?)"', f.read())
        if version:
            v = version.group(1)

    major, minor, patch = v.split(".")

    if to_bump == "patch":
        patch = str(int(patch) + 1)
    elif to_bump == "minor":
        patch = "0"
        minor = str(int(minor) + 1)
    elif to_bump == "major":
        patch = "0"
        minor = "0"
        major = str(int(major) + 1)

    new_version = f"{major}.{minor}.{patch}"

    files_to_update = ["PyPDFForm/__init__.py", "mkdocs.yml", "SECURITY.md"]

    for each in files_to_update:
        with open(each, encoding="utf8") as f:
            content = f.read().replace(v, new_version)

        os.remove(each)
        with open(each, mode="w", encoding="utf8") as f:
            f.write(content)
