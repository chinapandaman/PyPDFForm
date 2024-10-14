# -*- coding: utf-8 -*-
"""Builds package for release."""

import re

import setuptools

with open("PyPDFForm/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read())
    if version:
        version = version.group(1)

with open("README.md", mode="r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("prod_requirements.txt", mode="r", encoding="utf-8") as requirements:
    dependencies = [each.replace("\n", "") for each in requirements.readlines()]

setuptools.setup(
    name="PyPDFForm",
    version=version,
    description="The Python library for PDF forms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chinapandaman/PyPDFForm",
    author="Jinge Li",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=dependencies,
)
