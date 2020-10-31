# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements-deploy.txt", "r") as requirements:
    dependencies = [each.replace("\n", "") for each in requirements.readlines() if each]

setuptools.setup(
    name="PyPDFForm",
    version="0.0.5",
    author="Jinge Li",
    description="python library for PDF forms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chinapandaman/PyPDFForm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=dependencies,
)
