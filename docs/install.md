# Installation

PyPDFForm is available on [PyPI](https://pypi.org/project/PyPDFForm/) and can be installed using any preferred package manager, such as pip, Poetry, or uv.

## Prerequisites

PyPDFForm officially supports Python 3.10 and newer versions that are currently in their active life cycles. This typically includes the minimum supported version and the four major versions above it. For details on Python version life cycles, refer to [this page](https://devguide.python.org/versions/).

## Install the library

It is highly recommended to create a virtual environment before installation. Then, run the following command to install the PyPDFForm library:

```shell
pip install PyPDFForm
```

## Install the CLI

The CLI is packaged as the optional `cli` extra. For command-line use, [pipx](https://pipx.pypa.io/stable/) is recommended because it installs the command in an isolated environment and makes it available on your PATH:

```shell
pipx install "PyPDFForm[cli]"
```

After installation, run the following command to verify the CLI version:

```shell
pypdfform --version
```
