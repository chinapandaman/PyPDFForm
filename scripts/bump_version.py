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

    with open("PyPDFForm/__init__.py", encoding="utf8") as f:
        version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

    new_version = ".".join(
        version.split(".")[:-1] + [str(int(version.split(".")[-1]) + 1)]
    )

    with open("PyPDFForm/__init__.py", encoding="utf8") as f:
        content = f.read().replace(version, new_version)

    os.remove("PyPDFForm/__init__.py")
    with open("PyPDFForm/__init__.py", mode="w", encoding="utf8") as f:
        f.write(content)

    with open("mkdocs.yml", encoding="utf8") as f:
        content = f.read().replace(version, new_version)

    os.remove("mkdocs.yml")
    with open("mkdocs.yml", mode="w", encoding="utf8") as f:
        f.write(content)

    with open("SECURITY.md", encoding="utf8") as f:
        content = f.read().replace(version, new_version)

    os.remove("SECURITY.md")
    with open("SECURITY.md", mode="w", encoding="utf8") as f:
        f.write(content)
