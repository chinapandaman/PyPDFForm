# -*- coding: utf-8 -*-

import re

import setuptools

with open("PyPDFForm/__init__.py", encoding="utf8") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

dev_dependencies = ["coverage", "jsonschema", "pylint", "pytest"]

with open("requirements.txt", "r") as requirements:
    dependencies = [
        each.replace("\n", "")
        for each in requirements.readlines()
        if each.replace("\n", "") not in dev_dependencies
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
    python_requires=">=3.6",
    install_requires=dependencies,
)
