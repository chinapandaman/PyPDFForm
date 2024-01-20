# -*- coding: utf-8 -*-
"""Builds package for release."""

import re

import setuptools

with open("PyPDFForm/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with open("README.md", mode="r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("prod_requirements.txt", mode="r", encoding="utf-8") as requirements:
    dependencies = [
        each.replace("\n", "")
        for each in requirements.readlines()
    ]

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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=dependencies,
)
