# -*- coding: utf-8 -*-
"""Bumps a minor version."""

import os
import re

if __name__ == "__main__":
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
